"""
Django management command to migrate users from the Discord bot.

This script creates Django users for all users in the old Discord bot database,
setting them up to require a password reset on first login.

Usage:
    python manage.py migrate_discord_users

The script reads from the DISCORD_USERS list below (copied from Discord Users.txt).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from user.models import UserProfile


# Discord users data: (discord_id, first_name, last_name, username, email)
# Copied from Discord Users.txt
DISCORD_USERS = [
    (163856409534922752, 'David', 'Novick', 'dnovick', 'dnovick@sandiego.edu'),
    (167693722862092288, 'Taylor', 'Morgan Longo', 'tmorganlongo', 'tmorganlongo@sandiego.edu'),
    (181216855275470848, 'Marcus', 'Foy', 'mfoy', 'mfoy@sandiego.edu'),
    (183348154228408329, 'Rory', 'Gracey', 'rgracey', 'rgracey@sandiego.edu'),
    (225421713926520832, 'Andrew', 'Albizati', 'aalbizati', 'aalbizati@sandiego.edu'),
    (226542803813924865, 'Chris', 'Schafer', 'cschafer', 'cschafer@sandiego.edu'),
    (253471955611549697, 'Kyle', 'Abaya', 'kabaya', 'kabaya@sandiego.edu'),
    (279865658513293312, 'Connor', 'Jones', 'cnjones', 'cnjones@sandiego.edu'),
    (286016928856932352, 'Darrell', 'Morey', 'dmorey', 'dmorey@sandiego.edu'),
    (360496933841666059, 'Matthew', 'Limberg', 'mlimberg', 'mlimberg@sandiego.edu'),
    (417489237663940608, 'Monique', 'Nang', 'mnang', 'mnang@sandiego.edu'),
    (444956971540414464, 'Jason', 'Wiebke', 'jwiebke', 'jwiebke@sandiego.edu'),
    (466358050802892801, 'Sean', 'Limqueco', 'slimqueco', 'slimqueco@sandiego.edu'),
    (490615176274378753, 'Bilguun', 'Erdene Ochir', 'berdeneochir', 'berdeneochir@sandiego.edu'),
    (491108970199646229, 'Samantha', 'Stelter', 'sstelter', 'sstelter@sandiego.edu'),
    (494261418590470145, 'Kevin', 'Nhu', 'knhu', 'knhu@sandiego.edu'),
    (504800685989036062, 'Long', 'Pham', 'longpham', 'longpham@sandiego.edu'),
    (538798655092555789, 'Kai', 'Marshall', 'kaimarshall', 'kaimarshall@sandiego.edu'),
    (540375996050833411, 'Bryan', 'Ranzetta', 'branzetta', 'branzetta@sandiego.edu'),
    (545322146788802562, 'Charles', 'Fischer', 'charlesfischer', 'charlesfischer@sandiego.edu'),
    (545840735836962826, 'Karina', 'Marquez', 'kmarquez', 'kmarquez@sandiego.edu'),
    (579083719932117004, 'Gabe', 'S', 'gseidl', 'gseidl@sandiego.edu'),
    (595451486138269696, 'John', 'Phillips', 'johnphillips', 'johnphillips@sandiego.edu'),
    (690692605738221589, 'Camille', 'Abaya', 'cabaya', 'cabaya@sandiego.edu'),
    (696551359364726884, 'Dianne', 'Catapang', 'dcatapang', 'dcatapang@sandiego.edu'),
    (709969461137899540, 'Brennan', 'Martin', 'brennanmartin', 'brennanmartin@sandiego.edu'),
    (712833388452511825, 'Brian', 'Kim', 'donghyunkim', 'donghyunkim@sandiego.edu'),
    (750505714358812772, 'Jason', 'Reed', 'jasonreed', 'jasonreed@sandiego.edu'),
    (756761563418853386, 'Oscar', 'Gracias', 'ogracias', 'ogracias@sandiego.edu'),
    (759153639906082847, 'Ella', 'Moore', 'ellamoore', 'ellamoore@sandiego.edu'),
    (770429379658121263, 'Vy', 'Nguyen', 'vynguyen', 'vynguyen@sandiego.edu'),
    (775291238710509579, 'Phia', 'Leonard', 'sophialeonard', 'sophialeonard@sandiego.edu'),
    (801159979926421515, 'Chris', 'Perez', 'cnperez', 'cnperez@sandiego.edu'),
    (820108044750028821, 'Kristiana', 'Krasteva', 'kkrasteva', 'kkrasteva@sandiego.edu'),
    (861414230439362582, 'Gable', 'Krich', 'gkrich', 'gkrich@sandiego.edu'),
    (879485410533867590, 'Ethan', 'Chebi', 'echebi', 'echebi@sandiego.edu'),
    (891480661951676487, 'Michael', 'Bonn', 'mikebonn', 'mikebonn@sandiego.edu'),
    (898637108086988873, 'Marc', 'Carpio', 'mcarpio', 'mcarpio@sandiego.edu'),
    (915798364497514546, 'Andy', 'Chang', 'andychang', 'andychang@sandiego.edu'),
    (930519937871646791, 'Shaun', 'DeWitt', 'sdewitt', 'sdewitt@sandiego.edu'),
    (938912776083103754, 'Sydney', 'Stark', 'sydneystark', 'sydneystark@sandiego.edu'),
    (938915525067702322, 'Gab', 'Ramseier', 'gramseier', 'gramseier@sandiego.edu'),
    (939566307165237400, 'Sheyla', 'Aguilar', 'saguilar', 'saguilar@sandiego.edu'),
    (948320385575833671, 'Wanda', 'Young', 'wyoung', 'wyoung@sandiego.edu'),
    (986781507186208778, 'Lucas', 'Collins', 'lucascollins', 'lucascollins@sandiego.edu'),
    (1011763602434301992, 'Steven', 'Goodwin', 'sgoodwin', 'sgoodwin@sandiego.edu'),
    (1011764144577450044, 'Nikki', 'Monge', 'nmonge', 'nmonge@sandiego.edu'),
    (1011764603232977066, 'Liza', 'Nunes', 'lnunes', 'lnunes@sandiego.edu'),
    (1011764757424001185, 'Cade', 'McLean', 'cmclean', 'cmclean@sandiego.edu'),
    (1013932686609502229, 'Elizabeth', 'Mendoza', 'emendozaperez', 'emendozaperez@sandiego.edu'),
    (1026543836618571856, 'Andrew', 'Jockelle', 'ajockelle', 'ajockelle@sandiego.edu'),
    (1065774709356109954, 'Hiromi', 'Gonzalez', 'hgonzalez', 'hgonzalez@sandiego.edu'),
    (1070443723000922183, 'Emma', 'Cervi', 'ecervi', 'ecervi@sandiego.edu'),
    (1107882746099011694, 'Liam', 'Longpre', 'llongpre', 'llongpre@sandiego.edu'),
    (1113136250916974592, 'Kevin', 'Suimanjaya', 'ksuimanjaya', 'ksuimanjaya@sandiego.edu'),
    (1143604392508010577, 'Elsa', 'Pheif', 'epheif', 'epheif@sandiego.edu'),
    (1143606579887866007, 'Maggie', 'Cope', 'mcope', 'mcope@sandiego.edu'),
    (1207830879464853535, 'Natalia', 'Orlof-Carson', 'norlofcarson', 'norlofcarson@sandiego.edu'),
    (1278039323450671164, 'Mike', 'Oatis', 'moatis', 'moatis@sandiego.edu'),
    (1278039535611285600, 'Caden', 'Leonard', 'cadenleonard', 'cadenleonard@sandiego.edu'),
    (1278039592423129250, 'Sofia', 'Rea', 'srea', 'srea@sandiego.edu'),
    (1278039610483802354, 'Olivia', 'Frigyes', 'ofrigyes', 'ofrigyes@sandiego.edu'),
    (1278039625494954096, 'Toby', 'Bolcer', 'tbolcer', 'tbolcer@sandiego.edu'),
    (1278039671569383508, 'Tammy', 'Mathews', 'tmathews', 'tmathews@sandiego.edu'),
    (1331347887191490634, 'Matti', 'Homsi', 'mhomsi', 'mhomsi@sandiego.edu'),
    (1331349521296396433, 'Francis', 'Ortiz', 'fortiz', 'fortiz@sandiego.edu'),
    (1331349995613589599, 'Valeria', 'Negrete', 'valerianegrete', 'valerianegrete@sandiego.edu'),
    (1402491238233673869, 'Kassandra', 'Munoz', 'kassandramunoz', 'kassandramunoz@sandiego.edu'),
    (1409609677318393878, 'Mishi', 'Batinkova', 'mbatinkova', 'mbatinkova@sandiego.edu'),
    (1409609690614206494, 'Carter', 'Witten', 'cwitten', 'cwitten@sandiego.edu'),
    (1409609690685640836, 'Koa', 'Cruz', 'koacruz', 'koacruz@sandiego.edu'),
    (1409609746733858917, 'Miranda', 'Gallegos', 'mirandagallegos', 'mirandagallegos@sandiego.edu'),
    (1409609785480970243, 'Gabby', 'Dow', 'gdow', 'gdow@sandiego.edu'),
    (1409609791038292009, 'Michael', 'Acosta', 'michaelacosta', 'michaelacosta@sandiego.edu'),
    (1429949997616468048, 'Juliet', 'Roberto', 'jroberto', 'jroberto@sandiego.edu'),
    (1429959596365053972, 'Jackson', 'Kelley', 'jacksonkelley', 'jacksonkelley@sandiego.edu'),
    (1463216443142443160, 'Tyler', 'Hayes', 'tylerhayes', 'tylerhayes@sandiego.edu'),
    (1463258839129264213, 'Owen', 'Gray', 'ogray', 'ogray@sandiego.edu'),
]


class Command(BaseCommand):
    help = 'Migrate users from Discord bot to Django, setting them to require password reset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating users',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        self.stdout.write(self.style.NOTICE(f"{'DRY RUN - ' if dry_run else ''}Starting migration of {len(DISCORD_USERS)} Discord users..."))
        self.stdout.write("")
        
        for discord_id, first_name, last_name, username, email in DISCORD_USERS:
            # Check if user with this discord_id already exists
            existing_profile = UserProfile.objects.filter(discord_id=discord_id).first()
            if existing_profile:
                self.stdout.write(f"  SKIP: {first_name} {last_name} - Discord ID {discord_id} already exists (user: {existing_profile.user.username})")
                skipped_count += 1
                continue
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"  SKIP: {first_name} {last_name} - Username '{username}' already exists"))
                skipped_count += 1
                continue
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"  SKIP: {first_name} {last_name} - Email '{email}' already exists"))
                skipped_count += 1
                continue
            
            if dry_run:
                self.stdout.write(f"  WOULD CREATE: {first_name} {last_name} (username: {username}, email: {email}, discord_id: {discord_id})")
                created_count += 1
                continue
            
            try:
                # Create the user with an unusable password
                user = User.objects.create(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                user.set_unusable_password()
                user.save()
                
                # Create the profile with discord_id and must_reset_password=True
                UserProfile.objects.create(
                    user=user,
                    discord_id=discord_id,
                    must_reset_password=True,
                    migrated_at=timezone.now()
                )
                
                self.stdout.write(self.style.SUCCESS(f"  CREATED: {first_name} {last_name} (username: {username}, email: {email})"))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ERROR: {first_name} {last_name} - {str(e)}"))
                error_count += 1
        
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("=" * 50))
        self.stdout.write(self.style.SUCCESS(f"Created: {created_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write(self.style.NOTICE("=" * 50))
        
        if dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("This was a dry run. Run without --dry-run to create users."))
