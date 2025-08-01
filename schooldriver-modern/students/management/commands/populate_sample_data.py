from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from students.models import Student, GradeLevel, SchoolYear, EmergencyContact
from admissions.models import (
    Applicant,
    AdmissionLevel,
    AdmissionCheck,
    FeederSchool,
    ApplicationDecision,
    ContactLog,
    OpenHouse,
    ApplicantDocument,
)
from academics.models import (
    Department,
    Course,
    CourseSection,
    Enrollment,
    AssignmentCategory,
    Assignment,
    Grade,
    Schedule,
    Attendance,
    Announcement,
    Message,
)
import random
from django.db import transaction


class Command(BaseCommand):
    help = "Populate the database with realistic sample data for demonstration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing sample data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing sample data...")
            self.clear_sample_data()

        with transaction.atomic():
            self.stdout.write("Creating sample data...")
            self.create_grade_levels()
            self.create_school_years()
            self.create_admission_infrastructure()
            self.create_feeder_schools()
            self.create_sample_users()
            self.create_academic_infrastructure()
            self.create_sample_students()
            self.create_sample_applicants()
            self.create_sample_documents()
            self.create_open_houses()
            self.create_academic_data()
            self.create_sample_messages()

        self.stdout.write(
            self.style.SUCCESS(
                "\nSample data created successfully!\n"
                "Visit http://localhost:8000/admin to explore the data.\n"
                "Login with: admin / admin123"
            )
        )

    def clear_sample_data(self):
        """Clear existing sample data"""
        # Clear in dependency order to avoid foreign key constraints
        models_to_clear = [
            # Academic models first
            Message,
            Announcement,
            Attendance,
            Grade,
            Assignment,
            Schedule,
            Enrollment,
            CourseSection,
            Course,
            Department,
            AssignmentCategory,
            # Admission models
            ApplicantDocument,
            OpenHouse,
            ContactLog,
            Applicant,
            ApplicationDecision,
            EmergencyContact,
            Student,
            FeederSchool,
            AdmissionCheck,
            AdmissionLevel,
            SchoolYear,
            GradeLevel,
        ]

        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  Cleared {count} {model.__name__} records")

    def create_grade_levels(self):
        """Create standard K-12 grade levels"""
        grade_data = [
            ("K", "Kindergarten", 1),
            ("1", "1st Grade", 2),
            ("2", "2nd Grade", 3),
            ("3", "3rd Grade", 4),
            ("4", "4th Grade", 5),
            ("5", "5th Grade", 6),
            ("6", "6th Grade", 7),
            ("7", "7th Grade", 8),
            ("8", "8th Grade", 9),
            ("9", "9th Grade", 10),
            ("10", "10th Grade", 11),
            ("11", "11th Grade", 12),
            ("12", "12th Grade", 13),
        ]

        for name, display_name, order in grade_data:
            grade, created = GradeLevel.objects.get_or_create(
                name=name, defaults={"order": order}
            )
            if created:
                self.stdout.write(f"  Created grade level: {display_name}")

    def create_school_years(self):
        """Create school years for current and next year"""
        current_year = datetime.now().year

        years_data = [
            (
                f"{current_year - 1}-{current_year}",
                date(current_year - 1, 8, 15),
                date(current_year, 6, 15),
                False,
            ),
            (
                f"{current_year}-{current_year + 1}",
                date(current_year, 8, 15),
                date(current_year + 1, 6, 15),
                True,
            ),
            (
                f"{current_year + 1}-{current_year + 2}",
                date(current_year + 1, 8, 15),
                date(current_year + 2, 6, 15),
                False,
            ),
        ]

        for name, start_date, end_date, is_active in years_data:
            year, created = SchoolYear.objects.get_or_create(
                name=name,
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_active": is_active,
                },
            )
            if created:
                status = "ACTIVE" if is_active else ""
                self.stdout.write(f"  Created school year: {name} {status}")

    def create_admission_infrastructure(self):
        """Create admission levels and checks"""
        # Create admission levels
        levels_data = [
            ("Inquiry Received", "Initial inquiry from prospective family", 1),
            ("Application Submitted", "Formal application completed and submitted", 2),
            ("Documents Complete", "All required documents received and verified", 3),
            (
                "Interview Scheduled",
                "Family interview scheduled with admissions team",
                4,
            ),
            ("Interview Complete", "Family interview conducted and notes recorded", 5),
            ("Decision Made", "Admissions committee has made final decision", 6),
        ]

        for name, description, order in levels_data:
            level, created = AdmissionLevel.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "order": order,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  Created admission level: {name}")

        # Create admission checks for each level
        inquiry_level = AdmissionLevel.objects.filter(name="Inquiry Received").first()
        application_level = AdmissionLevel.objects.filter(
            name="Application Submitted"
        ).first()
        documents_level = AdmissionLevel.objects.filter(
            name="Documents Complete"
        ).first()
        interview_level = AdmissionLevel.objects.filter(
            name="Interview Scheduled"
        ).first()

        if inquiry_level and application_level and documents_level and interview_level:
            checks_data = [
                (
                    inquiry_level,
                    "Application Form",
                    "Online application form completed",
                    True,
                    True,
                ),
                (
                    documents_level,
                    "Birth Certificate",
                    "Copy of student birth certificate",
                    True,
                    True,
                ),
                (
                    documents_level,
                    "Previous School Records",
                    "Transcripts from previous school",
                    True,
                    True,
                ),
                (
                    documents_level,
                    "Immunization Records",
                    "Current immunization documentation",
                    True,
                    True,
                ),
                (
                    interview_level,
                    "Parent Interview",
                    "Interview with parents/guardians",
                    True,
                    True,
                ),
                (
                    interview_level,
                    "Student Assessment",
                    "Age-appropriate academic assessment",
                    False,
                    True,
                ),
                (
                    application_level,
                    "Reference Letters",
                    "Letters of recommendation (if applicable)",
                    False,
                    True,
                ),
                (
                    application_level,
                    "Financial Aid Application",
                    "Financial assistance documentation",
                    False,
                    True,
                ),
                (
                    documents_level,
                    "Special Needs Documentation",
                    "IEP or 504 plan if applicable",
                    False,
                    True,
                ),
            ]

            for level, name, description, is_required, is_active in checks_data:
                check, created = AdmissionCheck.objects.get_or_create(
                    name=name,
                    level=level,
                    defaults={
                        "description": description,
                        "is_required": is_required,
                        "is_active": is_active,
                    },
                )
                if created:
                    req_status = "REQUIRED" if is_required else "OPTIONAL"
                    self.stdout.write(
                        f"  Created admission check: {name} ({req_status})"
                    )

    def create_feeder_schools(self):
        """Create sample feeder schools"""
        schools_data = [
            ("Riverside Elementary School", "Public", "Riverside", "CA"),
            ("St. Mary's Catholic School", "Private", "Downtown", "CA"),
            ("Oak Valley Charter School", "Charter", "Oak Valley", "CA"),
            ("Montessori Learning Center", "Private", "Hillcrest", "CA"),
            ("Lincoln Elementary", "Public", "Lincoln District", "CA"),
            ("Bright Futures Preschool", "Private", "Suburbia", "CA"),
            ("Valley Waldorf School", "Private", "Valley View", "CA"),
            ("Home School Network", "Homeschool", "Various", "CA"),
        ]

        for name, school_type, city, state in schools_data:
            school, created = FeederSchool.objects.get_or_create(
                name=name,
                defaults={
                    "school_type": school_type,
                    "city": city,
                    "state": state,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  Created feeder school: {name}")

    def create_sample_students(self):
        """Create sample students with emergency contacts"""
        # Get required objects
        grade_levels = list(GradeLevel.objects.all())
        current_school_year = SchoolYear.objects.filter(is_active=True).first()

        if not grade_levels or not current_school_year:
            self.stdout.write(
                self.style.WARNING(
                    "Grade levels or school year not found. Skipping students."
                )
            )
            return

        # Expanded student data for more comprehensive testing
        students_data = [
            # Kindergarten (5-8 students)
            ("Emma", "Rose", "Johnson", "F", date(2018, 3, 15), "K", "Loves art and reading stories"),
            ("Mason", "Cole", "Smith", "M", date(2018, 7, 22), "K", "Curious about everything"),
            ("Olivia", "Grace", "Williams", "F", date(2018, 1, 10), "K", "Great with puzzles"),
            ("Ethan", "James", "Brown", "M", date(2018, 9, 8), "K", "Loves building blocks"),
            ("Ava", "Mae", "Jones", "F", date(2018, 5, 14), "K", "Natural leader"),
            
            # 1st Grade (6-8 students)
            ("Liam", "James", "Williams", "M", date(2017, 8, 22), "1", "Energetic and great at math"),
            ("Sophia", "Claire", "Davis", "F", date(2017, 4, 18), "1", "Loves reading aloud"),
            ("Jackson", "Lee", "Miller", "M", date(2017, 11, 5), "1", "Excellent problem solver"),
            ("Isabella", "Rose", "Wilson", "F", date(2017, 2, 28), "1", "Creative storyteller"),
            ("Lucas", "Ryan", "Moore", "M", date(2017, 6, 12), "1", "Helpful and kind"),
            ("Mia", "Faith", "Taylor", "F", date(2017, 10, 3), "1", "Artistic and imaginative"),
            
            # 2nd Grade (6-8 students)
            ("Sophia", "Grace", "Brown", "F", date(2016, 11, 10), "2", "Very social and creative"),
            ("Alexander", "Stone", "Anderson", "M", date(2016, 3, 25), "2", "Loves science books"),
            ("Emma", "Lynn", "Thomas", "F", date(2016, 8, 7), "2", "Math whiz"),
            ("William", "Cole", "Jackson", "M", date(2016, 12, 19), "2", "Great team player"),
            ("Charlotte", "Hope", "White", "F", date(2016, 5, 31), "2", "Excellent writer"),
            ("Daniel", "Cruz", "Harris", "M", date(2016, 9, 14), "2", "Loves animals"),
            
            # 3rd Grade (7-9 students)
            ("Noah", "Alexander", "Davis", "M", date(2015, 5, 30), "3", "Loves science experiments"),
            ("Diego", "Carlos", "Martinez", "M", date(2015, 8, 15), "3", "Bilingual student, loves soccer"),
            ("Abigail", "Rose", "Clark", "F", date(2015, 1, 22), "3", "Bookworm and artist"),
            ("Jacob", "Ryan", "Rodriguez", "M", date(2015, 11, 8), "3", "Future engineer"),
            ("Emily", "Grace", "Lewis", "F", date(2015, 4, 17), "3", "Compassionate leader"),
            ("Michael", "James", "Walker", "M", date(2015, 7, 29), "3", "Sports enthusiast"),
            ("Madison", "Claire", "Hall", "F", date(2015, 10, 11), "3", "Talented musician"),
            
            # 4th Grade (7-9 students)
            ("Olivia", "Marie", "Miller", "F", date(2014, 9, 18), "4", "Excellent reader and writer"),
            ("Benjamin", "Luke", "Allen", "M", date(2014, 2, 6), "4", "Science fair winner"),
            ("Chloe", "Faith", "Young", "F", date(2014, 6, 23), "4", "Drama club star"),
            ("Samuel", "Stone", "Hernandez", "M", date(2014, 12, 4), "4", "Chess champion"),
            ("Grace", "Anne", "King", "F", date(2014, 4, 15), "4", "Student council rep"),
            ("Andrew", "Cole", "Wright", "M", date(2014, 8, 27), "4", "Technology expert"),
            ("Natalie", "Rose", "Lopez", "F", date(2014, 11, 9), "4", "Environmental activist"),
            
            # 5th Grade (7-9 students)
            ("William", "Joseph", "Wilson", "M", date(2013, 12, 3), "5", "Team player, loves sports"),
            ("Aisha", "Fatima", "Hassan", "F", date(2013, 3, 12), "5", "New student from Virginia"),
            ("Connor", "Blake", "Scott", "M", date(2013, 7, 19), "5", "Debate team member"),
            ("Lily", "Hope", "Green", "F", date(2013, 1, 31), "5", "Volunteer coordinator"),
            ("Tyler", "James", "Adams", "M", date(2013, 9, 13), "5", "Band section leader"),
            ("Zoe", "Claire", "Baker", "F", date(2013, 5, 25), "5", "Math competition winner"),
            ("Hunter", "Ryan", "Gonzalez", "M", date(2013, 11, 7), "5", "Future programmer"),
            
            # 6th Grade (8-10 students)
            ("Ava", "Elizabeth", "Moore", "F", date(2012, 7, 25), "6", "Student council member"),
            ("Logan", "Stone", "Nelson", "M", date(2012, 2, 11), "6", "Science olympiad captain"),
            ("Aria", "Grace", "Carter", "F", date(2012, 10, 18), "6", "Choir soloist"),
            ("Caleb", "Cole", "Mitchell", "M", date(2012, 4, 3), "6", "History buff"),
            ("Stella", "Rose", "Perez", "F", date(2012, 8, 16), "6", "Art portfolio winner"),
            ("Mason", "Luke", "Roberts", "M", date(2012, 12, 29), "6", "Basketball team captain"),
            ("Hazel", "Faith", "Turner", "F", date(2012, 6, 8), "6", "School newspaper editor"),
            ("Owen", "James", "Phillips", "M", date(2012, 1, 21), "6", "Robotics club president"),
            
            # 7th Grade (8-10 students)
            ("James", "Robert", "Taylor", "M", date(2011, 4, 12), "7", "Band member, plays trumpet"),
            ("Raj", "Vikram", "Patel", "M", date(2011, 11, 5), "7", "Math team captain"),
            ("Scarlett", "Anne", "Campbell", "F", date(2011, 7, 27), "7", "Drama club lead"),
            ("Grayson", "Cole", "Parker", "M", date(2011, 3, 9), "7", "Track and field star"),
            ("Luna", "Claire", "Evans", "F", date(2011, 9, 22), "7", "Environmental club founder"),
            ("Nolan", "Ryan", "Edwards", "M", date(2011, 1, 14), "7", "Chess club champion"),
            ("Violet", "Grace", "Collins", "F", date(2011, 6, 30), "7", "Peer mediator"),
            ("Easton", "Stone", "Stewart", "M", date(2011, 10, 17), "7", "Technology mentor"),
            
            # 8th Grade (8-10 students)
            ("Isabella", "Claire", "Anderson", "F", date(2010, 10, 8), "8", "Drama club president"),
            ("Wyatt", "James", "Sanchez", "M", date(2010, 2, 24), "8", "Student body treasurer"),
            ("Nova", "Rose", "Morris", "F", date(2010, 8, 11), "8", "Science fair winner"),
            ("Kai", "Luke", "Rogers", "M", date(2010, 5, 28), "8", "Soccer team captain"),
            ("Autumn", "Faith", "Reed", "F", date(2010, 12, 15), "8", "Volunteer coordinator"),
            ("Miles", "Cole", "Cook", "M", date(2010, 7, 2), "8", "Debate team champion"),
            ("Iris", "Hope", "Bailey", "F", date(2010, 3, 19), "8", "Orchestra first chair"),
            ("Phoenix", "Ryan", "Rivera", "M", date(2010, 11, 6), "8", "Coding club founder"),
            
            # 9th Grade (8-10 students)
            ("Michael", "David", "Thomas", "M", date(2009, 2, 20), "9", "Varsity soccer player"),
            ("Sofia", "Grace", "Cooper", "F", date(2009, 9, 7), "9", "Honor society member"),
            ("Adrian", "Stone", "Richardson", "M", date(2009, 5, 23), "9", "Jazz band leader"),
            ("Layla", "Claire", "Cox", "F", date(2009, 12, 10), "9", "Yearbook editor"),
            ("Jaxon", "Cole", "Ward", "M", date(2009, 7, 26), "9", "Wrestling champion"),
            ("Sage", "Rose", "Torres", "F", date(2009, 4, 13), "9", "Model UN president"),
            ("River", "James", "Peterson", "M", date(2009, 11, 29), "9", "Theatre tech director"),
            ("Willow", "Faith", "Gray", "F", date(2009, 8, 16), "9", "Environmental activist"),
            
            # 10th Grade (8-10 students)
            ("Charlotte", "Anne", "Jackson", "F", date(2008, 6, 14), "10", "Honor roll student, debate team"),
            ("Asher", "Luke", "Ramirez", "M", date(2008, 1, 30), "10", "Robotics team captain"),
            ("Maya", "Hope", "James", "F", date(2008, 10, 17), "10", "National merit scholar"),
            ("Felix", "Ryan", "Watson", "M", date(2008, 4, 4), "10", "Tennis team champion"),
            ("Ivy", "Grace", "Brooks", "F", date(2008, 8, 21), "10", "Student government VP"),
            ("Atlas", "Stone", "Kelly", "M", date(2008, 12, 8), "10", "Academic decathlon winner"),
            ("Wren", "Claire", "Sanders", "F", date(2008, 5, 25), "10", "Art scholarship recipient"),
            ("Orion", "Cole", "Price", "M", date(2008, 9, 12), "10", "Science olympiad medalist"),
            
            # 11th Grade (8-10 students)
            ("Benjamin", "Samuel", "White", "M", date(2007, 1, 7), "11", "NHS member, volunteers at library"),
            ("Aurora", "Rose", "Bennett", "F", date(2007, 7, 24), "11", "Valedictorian candidate"),
            ("Silas", "James", "Wood", "M", date(2007, 3, 11), "11", "Eagle Scout recipient"),
            ("Serenity", "Faith", "Barnes", "F", date(2007, 11, 28), "11", "Community service leader"),
            ("Titan", "Luke", "Ross", "M", date(2007, 6, 15), "11", "Football team captain"),
            ("Echo", "Grace", "Henderson", "F", date(2007, 2, 2), "11", "Speech and debate champion"),
            ("Knox", "Ryan", "Coleman", "M", date(2007, 9, 19), "11", "Engineering internship"),
            ("Luna", "Hope", "Jenkins", "F", date(2007, 5, 6), "11", "Musical theatre lead"),
            
            # 12th Grade (8-10 students)
            ("Amelia", "Kate", "Harris", "F", date(2006, 4, 28), "12", "Student body president, headed to Stanford"),
            ("Maximus", "Stone", "Perry", "M", date(2006, 11, 14), "12", "Full scholarship to MIT"),
            ("Celeste", "Claire", "Powell", "F", date(2006, 8, 1), "12", "Class salutatorian"),
            ("Zander", "Cole", "Long", "M", date(2006, 1, 18), "12", "State champion swimmer"),
            ("Harmony", "Rose", "Patterson", "F", date(2006, 6, 5), "12", "Yale early admission"),
            ("Blaze", "Ryan", "Hughes", "M", date(2006, 10, 22), "12", "NASA internship recipient"),
            ("Seraphina", "Faith", "Flores", "F", date(2006, 3, 9), "12", "Perfect SAT score"),
            ("Storm", "James", "Washington", "M", date(2006, 7, 26), "12", "Rhodes Scholar finalist"),
        ]

        for (
            first_name,
            middle_name,
            last_name,
            gender,
            dob,
            grade_name,
            notes,
        ) in students_data:
            # Find the grade level
            grade_level = next((g for g in grade_levels if g.name == grade_name), None)
            if not grade_level:
                continue

            # Calculate graduation year (assuming K-12 progression)
            years_to_graduation = 13 - grade_level.order
            graduation_year = datetime.now().year + years_to_graduation

            # Create student
            student = Student.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=dob,
                grade_level=grade_level,
                graduation_year=graduation_year,
                enrollment_date=current_school_year.start_date,
                is_active=True,
                notes=notes,
                special_needs=random.choice(
                    ["", "", "", "IEP - Reading Support", "504 Plan - ADHD"]
                ),
            )

            # Create emergency contacts for each student
            self.create_emergency_contacts_for_student(student)

            self.stdout.write(
                f"  Created student: {first_name} {last_name} (Grade {grade_name})"
            )

    def create_emergency_contacts_for_student(self, student):
        """Create 2-3 emergency contacts for a student"""
        # Sample parent names and info
        parent_data = [
            (
                "mother",
                f"Jennifer {student.last_name}",
                f"jennifer.{student.last_name.lower()}@email.com",
            ),
            (
                "father",
                f"Michael {student.last_name}",
                f"michael.{student.last_name.lower()}@email.com",
            ),
            (
                "grandparent",
                f"Mary {student.last_name}",
                f"mary.{student.last_name.lower()}@email.com",
            ),
            ("other", "David Johnson", "david.johnson@email.com"),
            ("emergency", "Lisa Rodriguez", "lisa.rodriguez@email.com"),
        ]

        # Create 2-3 contacts per student
        num_contacts = random.randint(2, 3)
        selected_contacts = random.sample(parent_data, num_contacts)

        for i, (relationship, full_name, email) in enumerate(selected_contacts):
            # Split full name
            name_parts = full_name.split(" ")
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])

            contact = EmergencyContact.objects.create(
                first_name=first_name,
                last_name=last_name,
                relationship=relationship,
                email=email,
                phone_primary=f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                phone_secondary=f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                is_primary=(i == 0),  # First contact is primary
                street=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'First'])} Street",
                city="Private School City",
                state="CA",
                zip_code=f"{random.randint(90000, 99999)}",
            )

            student.emergency_contacts.add(contact)

        # Update cached contact info
        student.save()

    def create_sample_applicants(self):
        """Create sample applicants in various stages of admission"""
        # Get required objects
        grade_levels = list(GradeLevel.objects.all())
        admission_levels = list(
            AdmissionLevel.objects.filter(is_active=True).order_by("order")
        )
        admission_checks = list(AdmissionCheck.objects.filter(is_active=True))
        feeder_schools = list(FeederSchool.objects.filter(is_active=True))

        if not all([grade_levels, admission_levels, admission_checks, feeder_schools]):
            self.stdout.write(
                self.style.WARNING("Required objects not found. Skipping applicants.")
            )
            return

        # Sample applicant data
        applicants_data = [
            # Recent inquiries (early stage)
            (
                "Sarah",
                "Lynn",
                "Thompson",
                "F",
                date(2016, 5, 20),
                "K",
                0,
                ["Application Form"],
            ),
            ("Daniel", "Ray", "Garcia", "M", date(2015, 9, 12), "1", 0, []),
            # Applications submitted (mid-stage)
            (
                "Madison",
                "Hope",
                "Lee",
                "F",
                date(2014, 2, 8),
                "2",
                1,
                ["Application Form", "Birth Certificate"],
            ),
            (
                "Ethan",
                "Cole",
                "Rodriguez",
                "M",
                date(2013, 7, 15),
                "3",
                1,
                ["Application Form", "Birth Certificate", "Previous School Records"],
            ),
            # Documents complete (advanced stage)
            (
                "Grace",
                "Avery",
                "Kim",
                "F",
                date(2012, 11, 30),
                "4",
                2,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                ],
            ),
            (
                "Jacob",
                "Stone",
                "Nguyen",
                "M",
                date(2011, 4, 25),
                "5",
                2,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                ],
            ),
            # Interview scheduled (late stage)
            (
                "Chloe",
                "Faith",
                "Robinson",
                "F",
                date(2010, 8, 10),
                "6",
                3,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                    "Parent Interview",
                ],
            ),
            # Interview complete (very advanced)
            (
                "Austin",
                "Blake",
                "Clark",
                "M",
                date(2009, 1, 18),
                "7",
                4,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                    "Parent Interview",
                    "Student Assessment",
                ],
            ),
            # Decision made (final stage)
            (
                "Lily",
                "Rose",
                "Adams",
                "F",
                date(2008, 6, 3),
                "8",
                5,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                    "Parent Interview",
                ],
            ),
            (
                "Connor",
                "James",
                "Wright",
                "M",
                date(2007, 12, 14),
                "9",
                5,
                [
                    "Application Form",
                    "Birth Certificate",
                    "Previous School Records",
                    "Immunization Records",
                    "Parent Interview",
                    "Student Assessment",
                    "Reference Letters",
                ],
            ),
        ]

        for (
            first_name,
            middle_name,
            last_name,
            gender,
            dob,
            target_grade,
            level_index,
            completed_checks,
        ) in applicants_data:
            # Find target grade level
            grade_level = next(
                (g for g in grade_levels if g.name == target_grade), None
            )
            if not grade_level:
                continue

            # Get admission level
            level = (
                admission_levels[level_index]
                if level_index < len(admission_levels)
                else admission_levels[-1]
            )

            # Select a random feeder school
            feeder_school = random.choice(feeder_schools)

            # Create applicant
            applicant = Applicant.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=dob,
                applying_for_grade=grade_level,
                level=level,
                current_school=feeder_school,
                primary_parent_email=f"{first_name.lower()}.{last_name.lower()}@email.com",
                primary_parent_phone=f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                notes=f"Prospective {target_grade} student from {feeder_school.name}",
            )

            # Add completed checks
            for check_name in completed_checks:
                check = AdmissionCheck.objects.filter(name=check_name).first()
                if check:
                    applicant.completed_checks.add(check)

            # Create a contact log entry
            ContactLog.objects.create(
                applicant=applicant,
                contact_type="email",
                contacted_by="Admissions Office",
                summary=f"Initial inquiry received from {applicant.primary_parent_email}",
                follow_up_needed=True,
                follow_up_date=timezone.now().date()
                + timedelta(days=random.randint(1, 14)),
            )

            # Sometimes update with decision info if at decision level
            if level_index >= 4:  # Decision made level
                # First create decision types if they don't exist
                accepted_decision, created = ApplicationDecision.objects.get_or_create(
                    name="Accepted", defaults={"is_positive": True, "order": 1}
                )
                waitlisted_decision, created = (
                    ApplicationDecision.objects.get_or_create(
                        name="Waitlisted", defaults={"is_positive": False, "order": 2}
                    )
                )
                declined_decision, created = ApplicationDecision.objects.get_or_create(
                    name="Declined", defaults={"is_positive": False, "order": 3}
                )

                # Assign decision to applicant
                decision_choice = random.choice(
                    [
                        accepted_decision,
                        accepted_decision,
                        waitlisted_decision,
                        declined_decision,
                    ]
                )  # Bias toward accepted
                applicant.decision = decision_choice
                applicant.decision_date = (
                    timezone.now() - timedelta(days=random.randint(1, 14))
                ).date()
                applicant.decision_by = "Admissions Committee"
                applicant.save()

            self.stdout.write(
                f"  Created applicant: {first_name} {last_name} (Level: {level.name})"
            )

    def create_sample_documents(self):
        """Create sample document records for applicants"""
        # Sample document data
        document_samples = [
            ("birth_certificate", "Birth Certificate", "sample_birth_cert.pdf"),
            ("immunization_records", "Immunization Records", "immunization_record.pdf"),
            (
                "previous_school_records",
                "Transcript from Previous School",
                "school_transcript.pdf",
            ),
            ("special_needs_documentation", "IEP Document", "iep_document.pdf"),
        ]

        applicants = Applicant.objects.all()[
            :15
        ]  # Add documents to first 15 applicants

        for applicant in applicants:
            # Randomly assign 2-4 documents per applicant
            num_docs = random.randint(2, 4)
            selected_docs = random.sample(
                document_samples, min(num_docs, len(document_samples))
            )

            for doc_type, title, filename in selected_docs:
                # Find related admission check if it exists
                admission_check = AdmissionCheck.objects.filter(
                    name__icontains=doc_type.replace("_", " ")
                ).first()

                document = ApplicantDocument.objects.create(
                    applicant=applicant,
                    admission_check=admission_check,
                    document_type=doc_type,
                    title=f"{title} for {applicant.first_name} {applicant.last_name}",
                    uploaded_by="Admin User",
                    is_verified=random.choice(
                        [True, True, False]
                    ),  # Bias toward verified
                    notes=random.choice(
                        [
                            "Document received and processed",
                            "Clear copy received",
                            "Pending verification",
                            "Original document verified",
                            "",
                        ]
                    ),
                )

                if document.is_verified:
                    document.verified_by = "Staff Member"
                    document.verified_date = timezone.now() - timedelta(
                        days=random.randint(1, 10)
                    )
                    document.save()

                self.stdout.write(
                    f"    Added {doc_type} document for {applicant.first_name} {applicant.last_name}"
                )

    def create_open_houses(self):
        """Create sample open house events"""
        open_houses_data = [
            (
                "Fall Open House",
                "Join us for our annual fall open house! Tour campus, meet teachers, and learn about our programs.",
                timezone.now() + timedelta(days=30),
                timezone.now() + timedelta(days=30, hours=2),
            ),
            (
                "Spring Information Session",
                "Informational session for prospective families considering enrollment.",
                timezone.now() + timedelta(days=60),
                timezone.now() + timedelta(days=60, hours=1.5),
            ),
            (
                "New Family Orientation",
                "Orientation session for newly admitted families.",
                timezone.now() + timedelta(days=120),
                timezone.now() + timedelta(days=120, hours=1),
            ),
        ]

        for name, description, start_time, end_time in open_houses_data:
            event = OpenHouse.objects.create(
                name=name,
                description=description,
                date=start_time,
                is_active=True,
                capacity=50,
            )
            self.stdout.write(f"  Created open house: {name}")

        # Summary statistics
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SAMPLE DATA SUMMARY:")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Grade Levels: {GradeLevel.objects.count()}")
        self.stdout.write(f"School Years: {SchoolYear.objects.count()}")
        self.stdout.write(f"Students: {Student.objects.count()}")
        self.stdout.write(f"Emergency Contacts: {EmergencyContact.objects.count()}")
        self.stdout.write(f"Applicants: {Applicant.objects.count()}")
        self.stdout.write(f"Admission Levels: {AdmissionLevel.objects.count()}")
        self.stdout.write(f"Admission Checks: {AdmissionCheck.objects.count()}")
        self.stdout.write(f"Feeder Schools: {FeederSchool.objects.count()}")
        self.stdout.write(f"Open Houses: {OpenHouse.objects.count()}")
        self.stdout.write(f"Contact Logs: {ContactLog.objects.count()}")
        self.stdout.write(
            f"Application Decisions: {ApplicationDecision.objects.count()}"
        )
        self.stdout.write(f"Applicant Documents: {ApplicantDocument.objects.count()}")
        self.stdout.write(f"Departments: {Department.objects.count()}")
        self.stdout.write(f"Courses: {Course.objects.count()}")
        self.stdout.write(f"Course Sections: {CourseSection.objects.count()}")
        self.stdout.write(f"Enrollments: {Enrollment.objects.count()}")
        self.stdout.write(f"Assignments: {Assignment.objects.count()}")
        self.stdout.write(f"Grades: {Grade.objects.count()}")
        self.stdout.write(f"Schedules: {Schedule.objects.count()}")
        self.stdout.write(f"Attendance Records: {Attendance.objects.count()}")
        self.stdout.write(f"Announcements: {Announcement.objects.count()}")
        self.stdout.write(f"Messages: {Message.objects.count()}")

    def create_sample_users(self):
        """Create sample teachers and parent users"""
        # Create teacher users
        teacher_data = [
            ("john.johnson", "John", "Johnson", "john.johnson@school.edu"),
            ("mary.davis", "Mary", "Davis", "mary.davis@school.edu"),
            ("robert.smith", "Robert", "Smith", "robert.smith@school.edu"),
            ("susan.wilson", "Susan", "Wilson", "susan.wilson@school.edu"),
            ("michael.brown", "Michael", "Brown", "michael.brown@school.edu"),
            ("lisa.garcia", "Lisa", "Garcia", "lisa.garcia@school.edu"),
            ("david.martinez", "David", "Martinez", "david.martinez@school.edu"),
            ("jennifer.taylor", "Jennifer", "Taylor", "jennifer.taylor@school.edu"),
        ]

        for username, first_name, last_name, email in teacher_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("teacher123")
                user.save()
                self.stdout.write(f"  Created teacher user: {username}")

    def create_academic_infrastructure(self):
        """Create departments, courses, and assignment categories"""
        # Create departments
        departments_data = [
            ("Mathematics", "Mathematics and Algebra Department"),
            ("English", "English Language Arts Department"),
            ("Science", "Science and Laboratory Department"),
            ("Social Studies", "History and Social Sciences Department"),
            ("Arts", "Visual and Performing Arts Department"),
            ("Physical Education", "Physical Education and Health Department"),
            ("Foreign Languages", "World Languages Department"),
            ("Technology", "Computer Science and Technology Department"),
        ]

        for name, description in departments_data:
            # Get a random teacher as head
            teachers = User.objects.filter(
                username__endswith=(".johnson", ".davis", ".smith", ".wilson")
            )
            head = random.choice(teachers) if teachers else None

            dept, created = Department.objects.get_or_create(
                name=name, defaults={"description": description, "head": head}
            )
            if created:
                self.stdout.write(f"  Created department: {name}")

        # Create courses
        courses_data = [
            # Elementary/Middle School
            (
                "MATH-K",
                "Kindergarten Math",
                "Mathematics",
                "Basic counting and number concepts",
            ),
            (
                "MATH-1",
                "1st Grade Math",
                "Mathematics",
                "Addition and subtraction basics",
            ),
            (
                "MATH-2",
                "2nd Grade Math",
                "Mathematics",
                "Multi-digit addition and subtraction",
            ),
            (
                "MATH-3",
                "3rd Grade Math",
                "Mathematics",
                "Multiplication and division introduction",
            ),
            ("MATH-4", "4th Grade Math", "Mathematics", "Fractions and decimals"),
            (
                "MATH-5",
                "5th Grade Math",
                "Mathematics",
                "Advanced arithmetic and pre-algebra concepts",
            ),
            (
                "MATH-6",
                "6th Grade Math",
                "Mathematics",
                "Ratios, proportions, and beginning algebra",
            ),
            (
                "MATH-7",
                "7th Grade Math",
                "Mathematics",
                "Linear equations and geometry",
            ),
            (
                "MATH-8",
                "8th Grade Math",
                "Mathematics",
                "Advanced algebra and coordinate geometry",
            ),
            # High School Math
            ("ALG1", "Algebra I", "Mathematics", "Fundamental algebraic concepts"),
            ("GEO", "Geometry", "Mathematics", "Plane and solid geometry"),
            ("ALG2", "Algebra II", "Mathematics", "Advanced algebraic functions"),
            ("PRECALC", "Pre-Calculus", "Mathematics", "Preparation for calculus"),
            ("CALC", "Calculus", "Mathematics", "Differential and integral calculus"),
            # English
            (
                "ENG-K",
                "Kindergarten Reading",
                "English",
                "Letter recognition and phonics",
            ),
            ("ENG-1", "1st Grade Reading", "English", "Beginning reading skills"),
            (
                "ENG-2",
                "2nd Grade Reading",
                "English",
                "Reading comprehension development",
            ),
            (
                "ENG-3",
                "3rd Grade Language Arts",
                "English",
                "Reading fluency and writing basics",
            ),
            (
                "ENG-4",
                "4th Grade Language Arts",
                "English",
                "Literature and creative writing",
            ),
            (
                "ENG-5",
                "5th Grade Language Arts",
                "English",
                "Advanced reading and grammar",
            ),
            (
                "ENG-6",
                "6th Grade Language Arts",
                "English",
                "Literary analysis introduction",
            ),
            (
                "ENG-7",
                "7th Grade Language Arts",
                "English",
                "Writing and research skills",
            ),
            ("ENG-8", "8th Grade Language Arts", "English", "Advanced composition"),
            ("ENG9", "English 9", "English", "World literature and composition"),
            ("ENG10", "English 10", "English", "American literature"),
            ("ENG11", "English 11", "English", "British literature"),
            ("ENG12", "English 12", "English", "Advanced composition and literature"),
            # Science
            ("SCI-K", "Kindergarten Science", "Science", "Basic science concepts"),
            ("SCI-1", "1st Grade Science", "Science", "Plants, animals, and weather"),
            ("SCI-2", "2nd Grade Science", "Science", "Life cycles and matter"),
            ("SCI-3", "3rd Grade Science", "Science", "Earth science basics"),
            ("SCI-4", "4th Grade Science", "Science", "Energy and motion"),
            ("SCI-5", "5th Grade Science", "Science", "Physical science introduction"),
            ("SCI-6", "6th Grade Science", "Science", "Earth and space science"),
            ("SCI-7", "7th Grade Science", "Science", "Life science"),
            ("SCI-8", "8th Grade Science", "Science", "Physical science"),
            ("BIO", "Biology", "Science", "High school biology"),
            ("CHEM", "Chemistry", "Science", "High school chemistry"),
            ("PHYS", "Physics", "Science", "High school physics"),
            # Social Studies
            (
                "SS-K",
                "Kindergarten Social Studies",
                "Social Studies",
                "Community helpers and families",
            ),
            (
                "SS-1",
                "1st Grade Social Studies",
                "Social Studies",
                "School and neighborhood",
            ),
            (
                "SS-2",
                "2nd Grade Social Studies",
                "Social Studies",
                "Communities and citizenship",
            ),
            (
                "SS-3",
                "3rd Grade Social Studies",
                "Social Studies",
                "Local communities and geography",
            ),
            (
                "SS-4",
                "4th Grade Social Studies",
                "Social Studies",
                "State history and geography",
            ),
            (
                "SS-5",
                "5th Grade Social Studies",
                "Social Studies",
                "United States history",
            ),
            (
                "SS-6",
                "6th Grade Social Studies",
                "Social Studies",
                "Ancient civilizations",
            ),
            ("SS-7", "7th Grade Social Studies", "Social Studies", "World history"),
            ("SS-8", "8th Grade Social Studies", "Social Studies", "American history"),
            ("HIST9", "World History", "Social Studies", "High school world history"),
            ("HIST10", "US History", "Social Studies", "American history"),
            ("GOV", "Government", "Social Studies", "Civics and government"),
            ("ECON", "Economics", "Social Studies", "Economic principles"),
            # Arts
            ("ART-K", "Kindergarten Art", "Arts", "Basic art concepts and creativity"),
            ("ART-EL", "Elementary Art", "Arts", "Drawing, painting, and sculpture"),
            ("ART-MS", "Middle School Art", "Arts", "Advanced art techniques"),
            ("ART-HS", "High School Art", "Arts", "Portfolio development"),
            ("MUSIC-EL", "Elementary Music", "Arts", "Basic music concepts"),
            ("BAND", "Band", "Arts", "Instrumental music"),
            ("CHOIR", "Choir", "Arts", "Vocal music"),
            # PE
            (
                "PE-EL",
                "Elementary PE",
                "Physical Education",
                "Basic movement and games",
            ),
            (
                "PE-MS",
                "Middle School PE",
                "Physical Education",
                "Team sports and fitness",
            ),
            (
                "PE-HS",
                "High School PE",
                "Physical Education",
                "Advanced fitness and sports",
            ),
            ("HEALTH", "Health", "Physical Education", "Health and wellness education"),
        ]

        for course_code, name, dept_name, description in courses_data:
            department = Department.objects.filter(name=dept_name).first()
            if department:
                course, created = Course.objects.get_or_create(
                    course_code=course_code,
                    defaults={
                        "name": name,
                        "department": department,
                        "description": description,
                        "credit_hours": 1.0,
                    },
                )
                if created:
                    self.stdout.write(f"  Created course: {course_code}")

        # Create assignment categories
        categories_data = [
            ("Homework", "Daily homework assignments", 0.20),
            ("Quiz", "Short assessments", 0.15),
            ("Test", "Major assessments", 0.40),
            ("Project", "Long-term projects", 0.15),
            ("Participation", "Class participation and engagement", 0.10),
            ("Essay", "Written essays and reports", 0.25),
            ("Lab", "Laboratory work and experiments", 0.20),
            ("Presentation", "Oral presentations", 0.15),
        ]

        for name, description, weight in categories_data:
            category, created = AssignmentCategory.objects.get_or_create(
                name=name,
                defaults={"description": description, "default_weight": weight},
            )
            if created:
                self.stdout.write(f"  Created assignment category: {name}")

    def create_academic_data(self):
        """Create course sections, enrollments, assignments, grades, schedules, and attendance"""
        current_school_year = SchoolYear.objects.filter(is_active=True).first()
        if not current_school_year:
            self.stdout.write(
                self.style.WARNING(
                    "No active school year found. Skipping academic data."
                )
            )
            return

        # Create course sections for active students
        students = Student.objects.filter(is_active=True)
        teachers = User.objects.filter(username__contains=".")[:8]  # Get teacher users

        if not teachers:
            self.stdout.write(
                self.style.WARNING("No teacher users found. Skipping academic data.")
            )
            return

        # Group students by grade level
        students_by_grade = {}
        for student in students:
            if student.grade_level:  # Check if grade_level exists
                grade = student.grade_level.name
                if grade not in students_by_grade:
                    students_by_grade[grade] = []
                students_by_grade[grade].append(student)
            else:
                self.stdout.write(f"  Warning: Student {student.first_name} {student.last_name} has no grade level")

        # Create sections for each grade
        sections_created = []
        for grade, grade_students in students_by_grade.items():
            # Get appropriate courses for this grade
            grade_courses = Course.objects.filter(
                course_code__endswith=f"-{grade}"
            ) | Course.objects.filter(course_code__endswith=grade)

            # For high school grades, also include non-grade-specific courses
            if grade in ["9", "10", "11", "12"]:
                hs_courses = Course.objects.filter(
                    course_code__in=[
                        "ALG1",
                        "GEO",
                        "ALG2",
                        "PRECALC",
                        "CALC",
                        "ENG9",
                        "ENG10",
                        "ENG11",
                        "ENG12",
                        "BIO",
                        "CHEM",
                        "PHYS",
                        "HIST9",
                        "HIST10",
                        "GOV",
                        "ECON",
                        "ART-HS",
                        "PE-HS",
                    ]
                )
                grade_courses = grade_courses | hs_courses

            # For middle school
            elif grade in ["6", "7", "8"]:
                ms_courses = Course.objects.filter(
                    course_code__in=["ART-MS", "PE-MS", "BAND", "CHOIR"]
                )
                grade_courses = grade_courses | ms_courses

            # For elementary
            else:
                el_courses = Course.objects.filter(
                    course_code__in=["ART-EL", "PE-EL", "MUSIC-EL"]
                )
                grade_courses = grade_courses | el_courses

            for course in grade_courses[:8]:  # Limit to 8 courses per grade
                teacher = random.choice(teachers)

                section, created = CourseSection.objects.get_or_create(
                    course=course,
                    school_year=current_school_year,
                    section_name="A",
                    defaults={
                        "teacher": teacher,
                        "room": f"Room {random.randint(100, 299)}",
                        "max_students": 25,
                    },
                )
                if created:
                    sections_created.append(section)
                    self.stdout.write(f"  Created section: {section}")

                    # Enroll students in this section
                    for student in grade_students:
                        Enrollment.objects.get_or_create(
                            student=student, section=section
                        )

                    # Create schedule for this section
                    days = ["MON", "TUE", "WED", "THU", "FRI"]
                    start_times = [
                        "08:00",
                        "09:00",
                        "10:00",
                        "11:00",
                        "13:00",
                        "14:00",
                        "15:00",
                    ]

                    for day in random.sample(days, 3):  # 3 days per week
                        start_time = random.choice(start_times)
                        Schedule.objects.get_or_create(
                            section=section,
                            day_of_week=day,
                            start_time=start_time,
                            end_time=f"{int(start_time[:2]) + 1:02d}:00",
                            room=section.room,
                        )

        # Create assignments and grades
        categories = list(AssignmentCategory.objects.all())
        if not categories:
            self.stdout.write(
                self.style.WARNING(
                    "No assignment categories found. Skipping assignments."
                )
            )
            return

        assignment_templates = [
            "Quiz 1", "Quiz 2", "Quiz 3", "Quiz 4", "Quiz 5",
            "Test 1", "Test 2", "Test 3", "Midterm Exam", "Final Exam",
            "Homework Set 1", "Homework Set 2", "Homework Set 3", "Homework Set 4", 
            "Homework Set 5", "Daily Practice 1", "Daily Practice 2", "Daily Practice 3",
            "Project 1", "Final Project", "Group Project", "Science Fair Project",
            "Research Paper", "Book Report", "Current Events Essay", "Creative Writing",
            "Lab Report 1", "Lab Report 2", "Lab Report 3", "Field Study Report",
            "Class Presentation", "Group Presentation", "Oral Report", "Speech",
            "Math Problem Set", "Word Problems", "Geometry Practice", "Algebra Review",
            "Reading Comprehension", "Vocabulary Quiz", "Grammar Test", "Spelling Test",
            "Art Portfolio", "Creative Project", "Design Challenge", "Craft Assignment",
            "PE Skills Test", "Fitness Assessment", "Sports Performance", "Health Quiz",
            "Science Experiment", "Nature Observation", "Lab Practical", "Research Study",
            "History Timeline", "Geography Map", "Government Report", "Economics Project",
        ]

        for section in sections_created:  # Process all sections for fuller data
            # Create 10-15 assignments per section for comprehensive testing
            num_assignments = random.randint(10, 15)

            for i in range(num_assignments):
                assignment_name = random.choice(assignment_templates)
                category = random.choice(categories)

                # Create assignments with varied due dates for better testing
                today = timezone.now().date()
                assignment_type = random.choice(
                    [
                        "past_graded",
                        "past_submitted",
                        "past_missing",
                        "upcoming",
                        "today",
                    ]
                )

                if assignment_type == "past_graded":
                    assigned_date = today - timedelta(days=random.randint(7, 30))
                    due_date = assigned_date + timedelta(days=random.randint(3, 7))
                elif assignment_type == "past_submitted":
                    assigned_date = today - timedelta(days=random.randint(5, 20))
                    due_date = assigned_date + timedelta(days=random.randint(3, 7))
                elif assignment_type == "past_missing":
                    assigned_date = today - timedelta(days=random.randint(5, 15))
                    due_date = assigned_date + timedelta(days=random.randint(3, 7))
                elif assignment_type == "upcoming":
                    assigned_date = today - timedelta(days=random.randint(0, 5))
                    due_date = today + timedelta(days=random.randint(1, 14))
                else:  # today
                    assigned_date = today - timedelta(days=random.randint(3, 7))
                    due_date = today

                assignment = Assignment.objects.create(
                    section=section,
                    category=category,
                    name=f"{assignment_name} - {section.course.name}",
                    assigned_date=assigned_date,
                    due_date=due_date,
                    max_points=random.choice([10, 20, 50, 100]),
                    is_published=True,
                )

                # Create grades based on assignment type to ensure proper status distribution
                for enrollment in section.enrollments.all():
                    if assignment_type == "past_graded":
                        # Graded assignments - has points
                        points_earned = random.uniform(0.6, 1.0) * float(
                            assignment.max_points
                        )
                        is_late = random.random() < 0.1
                        Grade.objects.create(
                            enrollment=enrollment,
                            assignment=assignment,
                            points_earned=round(points_earned, 2),
                            is_late=is_late,
                            graded_by=section.teacher,
                            graded_date=due_date + timedelta(days=random.randint(1, 5)),
                        )
                    elif assignment_type == "past_submitted":
                        # Submitted but not graded - no points yet
                        if random.random() < 0.8:  # 80% submitted
                            Grade.objects.create(
                                enrollment=enrollment,
                                assignment=assignment,
                                points_earned=None,  # Submitted but not graded
                                is_late=random.random() < 0.1,
                                graded_by=None,
                                graded_date=None,
                            )
                    elif assignment_type == "past_missing":
                        # Missing assignments - no grade at all
                        if (
                            random.random() < 0.3
                        ):  # Only 30% have submitted (rest are missing)
                            points_earned = random.uniform(0.4, 0.8) * float(
                                assignment.max_points
                            )
                            Grade.objects.create(
                                enrollment=enrollment,
                                assignment=assignment,
                                points_earned=round(points_earned, 2),
                                is_late=True,
                                graded_by=section.teacher,
                                graded_date=due_date
                                + timedelta(days=random.randint(1, 10)),
                            )
                    # upcoming and today assignments have no grades (pending)

        # Create attendance records for the past 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        for enrollment in Enrollment.objects.all():  # Process all enrollments for complete attendance data
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday=0, Friday=4
                    status = random.choices(
                        ["P", "A", "T", "E"],
                        weights=[
                            85,
                            5,
                            8,
                            2,
                        ],  # 85% present, 5% absent, 8% tardy, 2% excused
                    )[0]

                    Attendance.objects.get_or_create(
                        enrollment=enrollment,
                        date=current_date,
                        defaults={
                            "status": status,
                            "recorded_by": enrollment.section.teacher,
                        },
                    )

                current_date += timedelta(days=1)

        # Create sample announcements
        announcements_data = [
            (
                "Welcome Back to School!",
                "We're excited to welcome all students back for the new school year. Please review the updated handbook and safety protocols.",
                "ALL",
            ),
            (
                "Parent-Teacher Conferences",
                "Parent-teacher conferences are scheduled for next week. Please check your email for your appointment time.",
                "PARENTS",
            ),
            (
                "Science Fair Registration",
                "The annual science fair is coming up! Students interested in participating should register by Friday.",
                "STUDENTS",
            ),
            (
                "Staff Meeting Reminder",
                "Monthly staff meeting is scheduled for this Friday at 3:30 PM in the main conference room.",
                "TEACHERS",
            ),
            (
                "Early Dismissal Notice",
                "School will dismiss early on Wednesday due to professional development. Dismissal time is 1:00 PM.",
                "ALL",
            ),
        ]

        for title, content, audience in announcements_data:
            Announcement.objects.create(
                title=title,
                content=content,
                audience=audience,
                is_published=True,
                publish_date=timezone.now(),
                created_by=random.choice(teachers)
                if teachers
                else User.objects.filter(is_superuser=True).first(),
            )

        self.stdout.write(f"  Created {len(sections_created)} course sections")
        self.stdout.write(f"  Created {Enrollment.objects.count()} enrollments")
        self.stdout.write(f"  Created {Assignment.objects.count()} assignments")
        self.stdout.write(f"  Created {Grade.objects.count()} grades")
        self.stdout.write(f"  Created {Schedule.objects.count()} schedules")
        self.stdout.write(f"  Created {Attendance.objects.count()} attendance records")
        self.stdout.write(f"  Created {Announcement.objects.count()} announcements")

    def create_sample_messages(self):
        """Create sample messages between teachers, students, and parents"""
        teachers = User.objects.filter(username__contains=".")[:8]
        students = Student.objects.filter(is_active=True)
        
        # Create some parent users for messaging
        parent_users = []
        for i, student in enumerate(students[:30]):  # Create parent users for first 30 students
            parent_user, created = User.objects.get_or_create(
                username=f"parent{i+1}",
                defaults={
                    'first_name': f"Parent{i+1}",
                    'last_name': student.last_name,
                    'email': f"parent{i+1}.{student.last_name.lower()}@email.com",
                    'is_active': True,
                }
            )
            if created:
                parent_user.set_password("parent123")
                parent_user.save()
            parent_users.append(parent_user)
        
        if not teachers or not students:
            self.stdout.write(
                self.style.WARNING("No teachers or students found. Skipping messages.")
            )
            return

        # Sample message data
        message_data = [
            ("Assignment Missing", 
             "Hello, I wanted to let you know that {student_name} has not submitted their math homework assignment that was due yesterday. Please encourage them to complete and submit it by tomorrow. Let me know if there are any issues at home that might be affecting their schoolwork."),
            
            ("Great Progress!", 
             "I'm pleased to inform you that {student_name} has been showing excellent progress in class this week. Their participation has improved significantly and they scored 95% on their recent science test. Keep up the great work!"),
             
            ("Parent Conference Request",
             "I would like to schedule a brief meeting to discuss {student_name}'s progress in English class. There are some strategies we could implement together to help improve their reading comprehension. Are you available next week?"),
             
            ("Behavior Concern",
             "I wanted to discuss {student_name}'s behavior in class today. They were having difficulty staying focused and disrupted the lesson several times. Let's work together to help them be more successful in the classroom."),
             
            ("Assignment Reminder",
             "Hi, just a friendly reminder that {student_name}'s research project is due this Friday. Make sure to include all the required components we discussed in class. Let me know if you need any help!"),
             
            ("Excellent Work!",
             "Great job on the presentation today! {student_name}'s research was thorough and they presented their findings very clearly. Keep up the outstanding work!"),
             
            ("Study Tips",
             "I noticed {student_name} is having some trouble with algebra equations. I've attached some extra practice problems that might help. Remember, my office hours are Tuesday and Thursday after school if you need additional help."),
             
            ("Field Trip Permission",
             "Don't forget to return your signed permission slip for next week's science museum field trip. We need all forms back by Friday. This will be a great educational experience!"),
             
            ("Picture Day Reminder",
             "School pictures will be taken next Tuesday, October 15th. Please make sure your student is dressed appropriately and arrives on time."),
             
            ("Report Cards Available",
             "Quarter report cards are now available in the parent portal. Please review your student's progress and don't hesitate to contact me if you have any questions about their grades."),
        ]

        # Create messages between teachers and parents
        messages_created = 0
        for i in range(50):  # Create 50 sample messages
            teacher = random.choice(teachers)
            
            if i < 30:  # Use students with parent users
                student = students[i % 30]
                parent = parent_users[i % 30]
            else:  # Create messages to any parent user
                student = random.choice(students[:30])
                parent = parent_users[students[:30].index(student)]
            
            subject, content_template = random.choice(message_data)
            
            # Fill in the student name in the template
            content = content_template.format(student_name=student.first_name)
            
            # Create the message
            message = Message.objects.create(
                sender=teacher,
                recipient=parent,
                subject=subject,
                content=content,
                is_read=random.choice([True, False]),
                is_urgent=random.choice([False, False, False, True]),  # 25% urgent
                student_context=student,
            )
            messages_created += 1
            
            # Some messages get replies
            if random.random() < 0.3:  # 30% get replies
                reply_content = random.choice([
                    f"Thank you for letting me know. I'll talk to {student.first_name} about this tonight.",
                    f"I appreciate you reaching out. {student.first_name} mentioned having some difficulty with this topic.",
                    f"Thank you for the update. We're very proud of {student.first_name}'s progress!",
                    f"I'll make sure {student.first_name} focuses on completing assignments on time.",
                    "Thank you for your message. I'd be happy to schedule a meeting to discuss this further.",
                    "We appreciate all your hard work with our child. Thank you for keeping us informed.",
                    f"I'll review {student.first_name}'s homework schedule with them this weekend.",
                ])
                
                reply = Message.objects.create(
                    sender=parent,
                    recipient=teacher,
                    subject=f"Re: {subject}",
                    content=reply_content,
                    parent_message=message,
                    is_read=random.choice([True, False]),
                    student_context=student,
                )
                messages_created += 1
        
        self.stdout.write(f"  Created {messages_created} messages")
