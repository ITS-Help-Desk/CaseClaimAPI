"""
Migrate case data from old CaseClaim Discord bot SQL dump to CaseClaimAPI.

Migrates:
  - CheckedClaims  -> ReviewedClaim
  - CompletedClaims -> CompleteClaim
  - ActiveClaims    -> ActiveClaim
  - Feedback        -> Used for ReviewedClaim comments

Usage:
  python manage.py migrate_case_data path/to/dump.sql
  python manage.py migrate_case_data path/to/dump.sql --dry-run
"""

import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from user.models import UserProfile
from reviewedclaim.models import ReviewedClaim
from completeclaim.models import CompleteClaim
from activeclaim.models import ActiveClaim


def parse_sql_values(sql_text, table_name):
    """
    Extract all INSERT rows for a given table from the SQL dump text.
    Returns a list of tuples, where each tuple is one row of raw string values.
    """
    pattern = rf"INSERT INTO `{table_name}` VALUES\n"
    rows = []

    chunks = sql_text.split(f"INSERT INTO `{table_name}` VALUES\n")
    if len(chunks) < 2:
        return rows

    for chunk in chunks[1:]:
        # Everything up to the terminating semicolon
        data_block = chunk.split(';\n')[0]
        rows.extend(parse_value_rows(data_block))

    return rows


def parse_value_rows(data_block):
    """
    Parse a block of SQL VALUES into a list of tuples.
    Handles quoted strings with escaped characters, NULLs, and integers.
    """
    rows = []
    i = 0
    length = len(data_block)

    while i < length:
        # Find the start of a row
        if data_block[i] == '(':
            values, end_pos = parse_single_row(data_block, i + 1)
            if values is not None:
                rows.append(tuple(values))
            i = end_pos + 1
        else:
            i += 1

    return rows


def parse_single_row(text, start):
    """Parse a single parenthesized row starting after the opening '('."""
    values = []
    i = start
    length = len(text)

    while i < length:
        # Skip whitespace
        while i < length and text[i] in (' ', '\t', '\n', '\r'):
            i += 1

        if i >= length:
            break

        if text[i] == ')':
            return values, i

        if text[i] == ',':
            i += 1
            continue

        if text[i] == "'":
            val, i = parse_quoted_string(text, i)
            values.append(val)
        elif text[i:i+4].upper() == 'NULL':
            values.append(None)
            i += 4
        else:
            # Numeric value
            end = i
            while end < length and text[end] not in (',', ')'):
                end += 1
            values.append(text[i:end].strip())
            i = end

    return values, i


def parse_quoted_string(text, start):
    """Parse a SQL quoted string starting at the opening quote."""
    i = start + 1
    length = len(text)
    chars = []

    while i < length:
        ch = text[i]
        if ch == '\\' and i + 1 < length:
            next_ch = text[i + 1]
            if next_ch == "'":
                chars.append("'")
            elif next_ch == '"':
                chars.append('"')
            elif next_ch == '\\':
                chars.append('\\')
            elif next_ch == 'n':
                chars.append('\n')
            elif next_ch == 'r':
                chars.append('\r')
            elif next_ch == 't':
                chars.append('\t')
            elif next_ch == '0':
                chars.append('\0')
            else:
                chars.append(next_ch)
            i += 2
        elif ch == "'" and i + 1 < length and text[i + 1] == "'":
            chars.append("'")
            i += 2
        elif ch == "'":
            return ''.join(chars), i + 1
        else:
            chars.append(ch)
            i += 1

    return ''.join(chars), i


def parse_timestamp(ts_str):
    """Parse a SQL timestamp string into a timezone-aware datetime."""
    if ts_str is None:
        return None
    ts_str = ts_str.strip()
    from datetime import timezone as dt_timezone
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.replace(tzinfo=dt_timezone.utc)
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = 'Migrate case data from old CaseClaim Discord bot SQL dump to CaseClaimAPI'

    def add_arguments(self, parser):
        parser.add_argument('sql_file', type=str, help='Path to the SQL dump file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without creating records',
        )

    def handle(self, *args, **options):
        sql_file = options['sql_file']
        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE(
            f"{'DRY RUN - ' if dry_run else ''}Loading SQL dump from: {sql_file}"
        ))

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_text = f.read()

        self.stdout.write("Parsing SQL dump...")

        # Build discord_id -> Django User mapping
        discord_to_user = self.build_user_mapping()

        # Parse Feedback table for comments/severity
        feedback_map = self.parse_feedback(sql_text)
        self.stdout.write(f"  Parsed {len(feedback_map)} Feedback records")

        # Migrate CheckedClaims -> ReviewedClaim
        self.migrate_reviewed_claims(sql_text, discord_to_user, feedback_map, dry_run)

        # Migrate CompletedClaims -> CompleteClaim
        self.migrate_complete_claims(sql_text, discord_to_user, dry_run)

        # Migrate ActiveClaims -> ActiveClaim
        self.migrate_active_claims(sql_text, discord_to_user, dry_run)

        self.stdout.write(self.style.SUCCESS("\nMigration complete!"))

    def build_user_mapping(self):
        """Build a mapping from discord_id to Django User object."""
        mapping = {}
        profiles = UserProfile.objects.select_related('user').exclude(discord_id__isnull=True)
        for profile in profiles:
            mapping[profile.discord_id] = profile.user

        self.stdout.write(f"  Built user mapping: {len(mapping)} discord_id -> User entries")
        return mapping

    def parse_feedback(self, sql_text):
        """Parse Feedback table into a dict: thread_id -> {severity, description}."""
        feedback_map = {}
        rows = parse_sql_values(sql_text, 'Feedback')

        for row in rows:
            # Feedback: (thread_id, message_id, severity, description)
            if len(row) < 4:
                continue
            thread_id = int(row[0])
            severity = row[2] if row[2] else ''
            description = row[3] if row[3] else ''
            feedback_map[thread_id] = {
                'severity': severity,
                'description': description,
            }

        return feedback_map

    def map_status(self, old_status, ping_thread_id, feedback_map):
        """
        Map old bot status to new CaseClaimAPI status.
        Old: Checked, Done, Kudos, Resolved, Pinged
        New: checked, done, kudos, resolved, pingedlow, pingedmed, pingedhigh, acknowledged
        """
        old_lower = old_status.lower().strip()

        if old_lower == 'checked':
            return 'checked'
        elif old_lower == 'done':
            return 'done'
        elif old_lower == 'kudos':
            return 'kudos'
        elif old_lower == 'resolved':
            # Resolved pings - determine severity from feedback
            if ping_thread_id and ping_thread_id in feedback_map:
                severity = feedback_map[ping_thread_id]['severity'].lower().strip()
                if severity in ('severe', 'high'):
                    return 'resolved'
                else:
                    return 'resolved'
            return 'resolved'
        elif old_lower == 'pinged':
            if ping_thread_id and ping_thread_id in feedback_map:
                severity = feedback_map[ping_thread_id]['severity'].lower().strip()
                if severity in ('low',):
                    return 'pingedlow'
                elif severity in ('moderate', 'medium', 'med'):
                    return 'pingedmed'
                elif severity in ('severe', 'high'):
                    return 'pingedhigh'
                else:
                    return 'pingedlow'
            return 'pingedlow'
        else:
            self.stdout.write(self.style.WARNING(f"    Unknown status '{old_status}', defaulting to 'checked'"))
            return 'checked'

    def get_comment(self, ping_thread_id, feedback_map):
        """Get the comment/description from Feedback if available."""
        if ping_thread_id and ping_thread_id in feedback_map:
            return feedback_map[ping_thread_id]['description']
        return ''

    def migrate_reviewed_claims(self, sql_text, discord_to_user, feedback_map, dry_run):
        """Migrate CheckedClaims -> ReviewedClaim."""
        self.stdout.write(self.style.NOTICE("\n--- Migrating CheckedClaims -> ReviewedClaim ---"))

        rows = parse_sql_values(sql_text, 'CheckedClaims')
        self.stdout.write(f"  Parsed {len(rows)} CheckedClaims rows")

        if not dry_run:
            existing_count = ReviewedClaim.objects.count()
            if existing_count > 0:
                self.stdout.write(self.style.WARNING(
                    f"  WARNING: {existing_count} ReviewedClaim records already exist. "
                    "Skipping duplicates by casenum + tech + lead + claim_time."
                ))

        created = 0
        skipped = 0
        errors = 0
        unmapped_users = set()

        # Temporarily disable auto_now_add on review_time so we can set historical values
        review_time_field = ReviewedClaim._meta.get_field('review_time')
        original_auto_now_add = review_time_field.auto_now_add
        if not dry_run:
            review_time_field.auto_now_add = False

        try:
            for row in rows:
                # CheckedClaims: (checker_message_id, case_num, tech_id, lead_id,
                #                  claim_time, complete_time, check_time, status, ping_thread_id)
                if len(row) < 8:
                    errors += 1
                    continue

                case_num = row[1]
                tech_discord_id = int(row[2])
                lead_discord_id = int(row[3])
                claim_time = parse_timestamp(row[4])
                complete_time = parse_timestamp(row[5])
                check_time = parse_timestamp(row[6])
                old_status = row[7]
                ping_thread_id = int(row[8]) if row[8] is not None else None

                # Map discord IDs to Django users
                tech_user = discord_to_user.get(tech_discord_id)
                lead_user = discord_to_user.get(lead_discord_id)

                if not tech_user:
                    unmapped_users.add(tech_discord_id)
                    skipped += 1
                    continue
                if not lead_user:
                    unmapped_users.add(lead_discord_id)
                    skipped += 1
                    continue

                new_status = self.map_status(old_status, ping_thread_id, feedback_map)
                comment = self.get_comment(ping_thread_id, feedback_map)

                if dry_run:
                    created += 1
                    continue

                # Check for duplicates
                if ReviewedClaim.objects.filter(
                    casenum=case_num,
                    tech_id=tech_user,
                    lead_id=lead_user,
                    claim_time=claim_time,
                ).exists():
                    skipped += 1
                    continue

                try:
                    rc = ReviewedClaim(
                        casenum=case_num,
                        tech_id=tech_user,
                        lead_id=lead_user,
                        claim_time=claim_time,
                        complete_time=complete_time,
                        review_time=check_time,
                        status=new_status,
                        comment=comment,
                        acknowledge_comment='',
                    )
                    rc.save()
                    created += 1
                except Exception as e:
                    errors += 1
                    if errors <= 10:
                        self.stdout.write(self.style.ERROR(
                            f"    Error on case {case_num}: {str(e)}"
                        ))

                if created % 1000 == 0 and created > 0:
                    self.stdout.write(f"    ...created {created} records so far")

        finally:
            # Restore auto_now_add
            review_time_field.auto_now_add = original_auto_now_add

        self.stdout.write(self.style.SUCCESS(f"  ReviewedClaim: {created} created, {skipped} skipped, {errors} errors"))
        if unmapped_users:
            self.stdout.write(self.style.WARNING(
                f"  Unmapped discord IDs (no Django user found): {unmapped_users}"
            ))

    def migrate_complete_claims(self, sql_text, discord_to_user, dry_run):
        """Migrate CompletedClaims -> CompleteClaim."""
        self.stdout.write(self.style.NOTICE("\n--- Migrating CompletedClaims -> CompleteClaim ---"))

        rows = parse_sql_values(sql_text, 'CompletedClaims')
        self.stdout.write(f"  Parsed {len(rows)} CompletedClaims rows")

        created = 0
        skipped = 0
        errors = 0

        # Temporarily disable auto_now_add on complete_time
        complete_time_field = CompleteClaim._meta.get_field('complete_time')
        original_auto_now_add = complete_time_field.auto_now_add
        if not dry_run:
            complete_time_field.auto_now_add = False

        try:
            for row in rows:
                # CompletedClaims: (checker_message_id, case_num, tech_id, claim_time, complete_time)
                if len(row) < 5:
                    errors += 1
                    continue

                case_num = row[1]
                tech_discord_id = int(row[2])
                claim_time = parse_timestamp(row[3])
                complete_time = parse_timestamp(row[4])

                tech_user = discord_to_user.get(tech_discord_id)
                if not tech_user:
                    self.stdout.write(self.style.WARNING(
                        f"    Skipping CompleteClaim {case_num}: tech discord_id {tech_discord_id} not found"
                    ))
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f"    WOULD CREATE: CompleteClaim {case_num} (tech: {tech_user.username})")
                    created += 1
                    continue

                if CompleteClaim.objects.filter(casenum=case_num, user_id=tech_user).exists():
                    self.stdout.write(f"    Skipping duplicate: {case_num}")
                    skipped += 1
                    continue

                try:
                    cc = CompleteClaim(
                        casenum=case_num,
                        user_id=tech_user,
                        lead_id=None,
                        claim_time=claim_time,
                        complete_time=complete_time,
                    )
                    cc.save()
                    created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"    CREATED: CompleteClaim {case_num} (tech: {tech_user.username})"
                    ))
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"    Error on case {case_num}: {str(e)}"))

        finally:
            complete_time_field.auto_now_add = original_auto_now_add

        self.stdout.write(self.style.SUCCESS(f"  CompleteClaim: {created} created, {skipped} skipped, {errors} errors"))

    def migrate_active_claims(self, sql_text, discord_to_user, dry_run):
        """Migrate ActiveClaims -> ActiveClaim."""
        self.stdout.write(self.style.NOTICE("\n--- Migrating ActiveClaims -> ActiveClaim ---"))

        rows = parse_sql_values(sql_text, 'ActiveClaims')
        self.stdout.write(f"  Parsed {len(rows)} ActiveClaims rows")

        created = 0
        skipped = 0
        errors = 0

        # Temporarily disable auto_now_add on claim_time
        claim_time_field = ActiveClaim._meta.get_field('claim_time')
        original_auto_now_add = claim_time_field.auto_now_add
        if not dry_run:
            claim_time_field.auto_now_add = False

        try:
            for row in rows:
                # ActiveClaims: (claim_message_id, case_num, tech_id, claim_time)
                if len(row) < 4:
                    errors += 1
                    continue

                case_num = row[1]
                tech_discord_id = int(row[2])
                claim_time = parse_timestamp(row[3])

                tech_user = discord_to_user.get(tech_discord_id)
                if not tech_user:
                    self.stdout.write(self.style.WARNING(
                        f"    Skipping ActiveClaim {case_num}: tech discord_id {tech_discord_id} not found"
                    ))
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f"    WOULD CREATE: ActiveClaim {case_num} (tech: {tech_user.username})")
                    created += 1
                    continue

                if ActiveClaim.objects.filter(casenum=case_num).exists():
                    self.stdout.write(f"    Skipping duplicate: {case_num}")
                    skipped += 1
                    continue

                try:
                    ac = ActiveClaim(
                        casenum=case_num,
                        user_id=tech_user,
                        claim_time=claim_time,
                    )
                    ac.save()
                    created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"    CREATED: ActiveClaim {case_num} (tech: {tech_user.username})"
                    ))
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"    Error on case {case_num}: {str(e)}"))

        finally:
            claim_time_field.auto_now_add = original_auto_now_add

        self.stdout.write(self.style.SUCCESS(f"  ActiveClaim: {created} created, {skipped} skipped, {errors} errors"))
