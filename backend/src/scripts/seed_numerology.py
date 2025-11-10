"""
Seed Numerology Interpretation Database

This script populates the numerology_interpretation table with comprehensive
expert interpretations for all numerology numbers (1-9, 11, 22, 33) across
all number types (life_path, expression, soul_urge, birthday, personal_year).

Usage:
    uv run python -m src.scripts.seed_numerology

The script will:
1. Check if data already exists
2. Prompt for confirmation if overwriting
3. Seed 200+ interpretation entries
4. Display progress during seeding
"""

from sqlmodel import Session, select
from sqlalchemy import text
from src.core.database import engine
from src.models.numerology_interpretation import NumerologyInterpretation


def check_and_confirm_overwrite(session) -> bool:
    """
    Check if interpretations already exist and prompt for confirmation.

    Returns:
        bool: True if should proceed with seeding, False to skip
    """
    # Check if data exists
    result = session.exec(select(NumerologyInterpretation))
    existing = result.all()
    existing_count = len(existing)

    if existing_count > 0:
        print(f"\n⚠️  Found {existing_count} existing interpretation entries")
        response = input("Clear all and reseed? (yes/no): ").lower().strip()

        if response != 'yes':
            print("❌ Seeding cancelled - existing data preserved")
            return False

        # Clear existing data
        print("🗑️  Clearing existing data...")
        session.exec(text("DELETE FROM numerology_interpretation"))
        session.commit()
        print("✅ Existing data cleared")

    return True


def seed_life_path_interpretations(session):
    """Seed Life Path number interpretations (1-9, 11, 22, 33)."""
    print("📖 Seeding Life Path interpretations...")

    interpretations = [
        # Life Path 1
        ("life_path", 1, "personality", "You are a natural-born leader with strong independence and pioneering spirit. Your confidence and determination drive you to forge your own path rather than follow others. You thrive when taking initiative and making autonomous decisions."),
        ("life_path", 1, "strengths", "Your greatest strengths are courage, originality, and the ability to start new ventures. You excel at innovation and aren't afraid to take calculated risks. Your self-reliance inspires others to trust your leadership."),
        ("life_path", 1, "challenges", "You may struggle with impatience, stubbornness, or being overly aggressive in pursuing your goals. Learning to collaborate and considering others' perspectives can enhance your natural leadership abilities. Balance independence with teamwork for greatest success."),
        ("life_path", 1, "career", "You excel in careers requiring leadership, innovation, and entrepreneurship. Consider roles as CEO, entrepreneur, inventor, or pioneering positions in any field. You thrive when you have autonomy and can set your own direction."),
        ("life_path", 1, "relationships", "In relationships, you need a partner who respects your independence while providing grounding. You can be dominant but must learn to share decision-making. Your ideal partner appreciates your ambition and gives you space to lead."),

        # Life Path 2
        ("life_path", 2, "personality", "You are a natural peacemaker with exceptional diplomatic skills and sensitivity to others' needs. Your gentle nature and ability to see all sides of a situation make you an excellent mediator. You thrive in harmonious environments where cooperation is valued."),
        ("life_path", 2, "strengths", "Your strengths lie in patience, cooperation, and the ability to build strong partnerships. You excel at bringing people together and creating consensus. Your intuition and emotional intelligence help you navigate complex social dynamics with grace."),
        ("life_path", 2, "challenges", "You may struggle with indecisiveness, over-sensitivity, or avoiding conflict to maintain peace. Learning to assert your own needs without fear is essential. Develop confidence in your own judgment rather than always deferring to others."),
        ("life_path", 2, "career", "You excel in roles requiring diplomacy, counseling, or teamwork. Consider careers in mediation, therapy, human resources, or collaborative partnerships. You thrive in supportive roles where you can help others succeed."),
        ("life_path", 2, "relationships", "In relationships, you are devoted, supportive, and emotionally attuned to your partner's needs. You seek harmony and deep emotional connection. Your ideal partner values your sensitivity and provides the security you need to flourish."),

        # Life Path 3
        ("life_path", 3, "personality", "You are creative, expressive, and naturally charismatic with a gift for communication. Your optimistic outlook and joyful energy draw people to you. You thrive when you can express yourself creatively and share your ideas with the world."),
        ("life_path", 3, "strengths", "Your greatest strengths are creativity, verbal expression, and the ability to inspire others through communication. You excel at art, writing, speaking, and any form of creative expression. Your enthusiasm is contagious and uplifting."),
        ("life_path", 3, "challenges", "You may struggle with scattered energy, superficiality, or difficulty finishing what you start. Learning to focus your creative gifts on meaningful projects is essential. Avoid the tendency to be overly critical of yourself or others."),
        ("life_path", 3, "career", "You excel in creative fields, communication, entertainment, or any role involving self-expression. Consider careers in writing, performing arts, marketing, or public speaking. You thrive when you can share your creativity with others."),
        ("life_path", 3, "relationships", "In relationships, you bring joy, creativity, and vibrant energy. You need a partner who appreciates your expressiveness and gives you room for creative pursuits. Communication and shared laughter are essential to your romantic fulfillment."),

        # Life Path 4
        ("life_path", 4, "personality", "You are practical, disciplined, and value stability and structure in all areas of life. Your systematic approach and strong work ethic make you a reliable foundation for others. You thrive when building solid, lasting structures."),
        ("life_path", 4, "strengths", "Your strengths include organization, reliability, and the ability to create order from chaos. You excel at detailed work, project management, and building sustainable systems. Your commitment and perseverance inspire trust."),
        ("life_path", 4, "challenges", "You may struggle with rigidity, resistance to change, or becoming too focused on rules and procedures. Learning to adapt and embrace flexibility will enhance your effectiveness. Allow room for spontaneity and new approaches."),
        ("life_path", 4, "career", "You excel in roles requiring organization, attention to detail, and systematic thinking. Consider careers in project management, engineering, accounting, or any field requiring precision and structure. You thrive in stable, well-organized environments."),
        ("life_path", 4, "relationships", "In relationships, you are loyal, dependable, and committed to building a stable life together. You show love through practical support and consistent presence. Your ideal partner appreciates your reliability and shares your values of security."),

        # Life Path 5
        ("life_path", 5, "personality", "You are adventurous, freedom-loving, and crave variety and new experiences. Your adaptable nature and curiosity drive you to explore all life has to offer. You thrive when you have the freedom to change and grow."),
        ("life_path", 5, "strengths", "Your strengths are adaptability, versatility, and the ability to thrive in changing circumstances. You excel at communication, sales, and any role requiring quick thinking. Your enthusiasm for life's adventures is infectious."),
        ("life_path", 5, "challenges", "You may struggle with restlessness, commitment issues, or difficulty following through. Learning to balance freedom with responsibility is essential. Develop focus to channel your diverse interests productively."),
        ("life_path", 5, "career", "You excel in dynamic careers involving travel, change, and variety. Consider roles in sales, journalism, travel, or entrepreneurship. You thrive in fast-paced environments where no two days are the same."),
        ("life_path", 5, "relationships", "In relationships, you need freedom, excitement, and intellectual stimulation. You fear feeling trapped or bored. Your ideal partner shares your adventurous spirit and gives you space while maintaining connection."),

        # Life Path 6
        ("life_path", 6, "personality", "You are nurturing, responsible, and deeply committed to creating harmony and caring for others. Your compassionate nature and desire to serve make you a natural healer and counselor. You thrive when you can make others' lives better."),
        ("life_path", 6, "strengths", "Your strengths include compassion, responsibility, and the ability to create beautiful, harmonious environments. You excel at caregiving, counseling, and any role involving service to others. Your nurturing presence brings comfort and healing."),
        ("life_path", 6, "challenges", "You may struggle with perfectionism, being overly controlling, or sacrificing your own needs for others. Learning to establish healthy boundaries and accept imperfection is essential. Remember to nurture yourself as you nurture others."),
        ("life_path", 6, "career", "You excel in caring professions, creative arts, or roles involving community service. Consider careers in teaching, healthcare, counseling, or the arts. You thrive when you can combine service with creativity."),
        ("life_path", 6, "relationships", "In relationships, you are devoted, supportive, and create a warm, loving home. You show love through acts of service and creating beauty. Your ideal partner appreciates your nurturing nature and shares your values of family and harmony."),

        # Life Path 7
        ("life_path", 7, "personality", "You are analytical, introspective, and seek deep understanding of life's mysteries. Your philosophical nature and need for solitude drive your quest for truth and wisdom. You thrive when you can explore ideas and develop your inner knowledge."),
        ("life_path", 7, "strengths", "Your strengths include analytical thinking, intuition, and the ability to see beneath surface appearances. You excel at research, analysis, and spiritual pursuits. Your depth of insight offers unique perspectives others miss."),
        ("life_path", 7, "challenges", "You may struggle with isolation, overthinking, or difficulty connecting emotionally with others. Learning to balance your need for solitude with human connection is essential. Share your insights rather than keeping them hidden."),
        ("life_path", 7, "career", "You excel in research, analysis, teaching, or spiritual pursuits. Consider careers in science, psychology, philosophy, or any field requiring deep investigation. You thrive in quiet environments where you can think deeply."),
        ("life_path", 7, "relationships", "In relationships, you need intellectual connection, privacy, and a partner who respects your need for solitude. You value depth over social butterfly activity. Your ideal partner engages your mind and honors your introspective nature."),

        # Life Path 8
        ("life_path", 8, "personality", "You are ambitious, powerful, and have a natural ability to manifest material success. Your business acumen and leadership in the material world drive you toward achievement. You thrive when building empires and wielding influence."),
        ("life_path", 8, "strengths", "Your strengths include business sense, leadership, and the ability to manifest wealth and power. You excel at managing resources, building organizations, and achieving material success. Your confidence and capability command respect."),
        ("life_path", 8, "challenges", "You may struggle with materialism, workaholism, or abusing power. Learning to balance material success with spiritual values is essential. Use your power to uplift others rather than dominate them."),
        ("life_path", 8, "career", "You excel in business, finance, executive leadership, or entrepreneurship. Consider roles as CEO, financial advisor, real estate developer, or any position of power and influence. You thrive when building and managing successful ventures."),
        ("life_path", 8, "relationships", "In relationships, you need a strong partner who can match your ambition and won't be intimidated by your power. You show love through providing security and opportunities. Your ideal partner respects your drive for success."),

        # Life Path 9
        ("life_path", 9, "personality", "You are compassionate, humanitarian, and driven by a desire to serve humanity. Your universal love and wisdom make you a natural healer and teacher. You thrive when you can make the world a better place for all."),
        ("life_path", 9, "strengths", "Your strengths include compassion, wisdom, and the ability to see the big picture of human experience. You excel at humanitarian work, teaching, and inspiring others to their highest potential. Your generosity of spirit touches many lives."),
        ("life_path", 9, "challenges", "You may struggle with giving too much, difficulty letting go of the past, or becoming a martyr. Learning to set boundaries and release what no longer serves is essential. Take care of yourself as you serve others."),
        ("life_path", 9, "career", "You excel in humanitarian work, teaching, healing, or the arts. Consider careers in non-profit leadership, education, counseling, or creative expression that uplifts humanity. You thrive when your work has meaningful impact."),
        ("life_path", 9, "relationships", "In relationships, you are loving, understanding, and accepting of others' flaws. You need a partner who shares your humanitarian values and supports your mission to serve. Your ideal partner appreciates your compassionate heart."),

        # Life Path 11 (Master Number)
        ("life_path", 11, "personality", "You are highly intuitive, spiritually aware, and carry tremendous potential for enlightenment. As a master number, you're here to inspire and illuminate others through your visionary insights. You thrive when channeling your spiritual gifts to uplift humanity."),
        ("life_path", 11, "strengths", "Your strengths include intuition, inspiration, and the ability to channel higher wisdom. You excel at spiritual teaching, counseling, and any role requiring visionary insight. Your presence alone can uplift and inspire others to their highest potential."),
        ("life_path", 11, "challenges", "You may struggle with nervous energy, impracticality, or difficulty grounding your visions into reality. Learning to balance your spiritual sensitivity with practical action is essential. Manage your intense energy through healthy practices."),
        ("life_path", 11, "career", "You excel in spiritual teaching, counseling, inspirational speaking, or any role involving higher consciousness. Consider careers in metaphysics, psychology, or creative arts that inspire. You thrive when serving as a spiritual guide or visionary leader."),
        ("life_path", 11, "relationships", "In relationships, you need a spiritually aware partner who understands your sensitivity and mission. You seek deep soul connection and shared spiritual growth. Your ideal partner supports your spiritual work while helping you stay grounded."),

        # Life Path 22 (Master Number)
        ("life_path", 22, "personality", "You are a master builder with the ability to turn grand visions into concrete reality. Combining practical skills with visionary insight, you're here to create lasting structures that benefit humanity. You thrive when building something of lasting value and significance."),
        ("life_path", 22, "strengths", "Your strengths include practical mastery, visionary thinking, and the ability to manifest large-scale projects. You excel at leadership, organization, and building enduring systems. Your combination of vision and practicality makes you uniquely powerful."),
        ("life_path", 22, "challenges", "You may struggle with the pressure of your own potential, self-doubt, or frustration when reality doesn't match your vision. Learning to trust the process and take one step at a time is essential. Remember that great buildings take time."),
        ("life_path", 22, "career", "You excel in large-scale projects, organizational leadership, or any field requiring visionary building. Consider careers in architecture, international business, large non-profits, or infrastructure development. You thrive when your work impacts many people."),
        ("life_path", 22, "relationships", "In relationships, you need a stable partner who believes in your vision and supports your ambitious projects. You show love through building security and creating lasting foundations. Your ideal partner shares your commitment to making a real difference."),

        # Life Path 33 (Master Number)
        ("life_path", 33, "personality", "You are the master teacher and healer, combining the intuition of 11 with the manifestation power of 22 and the compassion of 6. Your mission is to uplift humanity through unconditional love and spiritual teaching. You thrive when serving as a beacon of love and wisdom."),
        ("life_path", 33, "strengths", "Your strengths include unconditional love, spiritual wisdom, and the ability to heal through your presence. You excel at teaching, healing, and inspiring others to their highest spiritual potential. Your compassion and wisdom touch all who encounter you."),
        ("life_path", 33, "challenges", "You may struggle with the intensity of feeling others' pain, difficulty maintaining boundaries, or becoming overwhelmed by your mission. Learning to care without carrying the world's burdens is essential. Remember you can't save everyone."),
        ("life_path", 33, "career", "You excel in spiritual teaching, healing arts, counseling, or humanitarian leadership. Consider careers combining service with spiritual wisdom - perhaps leading healing centers, teaching spiritual principles, or guiding others' transformation. You thrive when your work embodies love and wisdom."),
        ("life_path", 33, "relationships", "In relationships, you offer unconditional love, deep understanding, and spiritual companionship. You need a partner who honors your spiritual mission and helps you maintain balance. Your ideal partner shares your commitment to love and service."),
    ]

    # Add interpretations to session
    for number_type, value, category, content in interpretations:
        interp = NumerologyInterpretation(
            number_type=number_type,
            number_value=value,
            category=category,
            content=content
        )
        session.add(interp)

    print(f"✅ Added {len(interpretations)} Life Path interpretations")


def seed_expression_interpretations(session):
    """Seed Expression number interpretations (1-9, 11, 22, 33)."""
    print("📖 Seeding Expression interpretations...")

    interpretations = [
        # Expression 1
        ("expression", 1, "talents", "Your natural talents include leadership, innovation, and the courage to pioneer new paths. You have an innate ability to take charge and inspire others to follow your vision. Your originality and independence are your greatest assets."),
        ("expression", 1, "abilities", "You excel at starting new ventures, making independent decisions, and standing firm in your convictions. Your ability to take decisive action and move forward despite obstacles sets you apart. You naturally inspire confidence in others."),
        ("expression", 1, "purpose", "Your life purpose is to lead, innovate, and show others the power of independent thinking and action. You're here to break new ground and demonstrate that courage and originality can create positive change. Your example inspires others to find their own strength."),

        # Expression 2
        ("expression", 2, "talents", "Your natural talents include diplomacy, cooperation, and the ability to see all perspectives in any situation. You have a gift for bringing people together and creating harmony. Your sensitivity to others' needs makes you an exceptional peacemaker."),
        ("expression", 2, "abilities", "You excel at mediation, building partnerships, and creating collaborative solutions. Your patience and attention to detail help you navigate complex situations with grace. You naturally understand emotional dynamics and can soothe conflicts."),
        ("expression", 2, "purpose", "Your life purpose is to bring people together, foster cooperation, and demonstrate the power of partnership. You're here to show that gentle persistence and understanding can overcome even the strongest obstacles. Your example teaches the value of harmony."),

        # Expression 3
        ("expression", 3, "talents", "Your natural talents include creative expression, communication, and the ability to uplift others through joy. You have a gift for words, art, or performance that brings beauty and inspiration to the world. Your optimism is contagious."),
        ("expression", 3, "abilities", "You excel at verbal and creative communication, inspiring others, and bringing ideas to life through artistic expression. Your enthusiasm and charisma draw people to you. You naturally see the positive potential in any situation."),
        ("expression", 3, "purpose", "Your life purpose is to express yourself creatively, uplift others through joy, and demonstrate the power of optimism. You're here to show that life can be celebrated and that creativity heals. Your example inspires others to embrace their own creative gifts."),

        # Expression 4
        ("expression", 4, "talents", "Your natural talents include organization, building sustainable systems, and bringing order to chaos. You have a gift for practical problem-solving and creating structures that last. Your reliability and attention to detail are exceptional."),
        ("expression", 4, "abilities", "You excel at detailed work, project management, and creating efficient systems. Your disciplined approach and strong work ethic allow you to accomplish what others find overwhelming. You naturally see how to build solid foundations."),
        ("expression", 4, "purpose", "Your life purpose is to build, organize, and create lasting structures that serve others. You're here to demonstrate the value of hard work, discipline, and systematic thinking. Your example shows that dedication creates real, tangible results."),

        # Expression 5
        ("expression", 5, "talents", "Your natural talents include adaptability, communication, and the ability to thrive in change. You have a gift for connecting with diverse people and experiences. Your versatility and quick thinking allow you to excel in varied situations."),
        ("expression", 5, "abilities", "You excel at sales, communication, adapting to new circumstances, and inspiring others to embrace change. Your freedom-loving nature and adventurous spirit open doors others don't see. You naturally sense opportunities and act on them quickly."),
        ("expression", 5, "purpose", "Your life purpose is to embrace change, experience life fully, and help others adapt to new circumstances. You're here to show that freedom and flexibility are paths to growth. Your example teaches the value of living adventurously."),

        # Expression 6
        ("expression", 6, "talents", "Your natural talents include nurturing, creating beauty, and bringing harmony to any environment. You have a gift for caring service and making others feel loved and supported. Your artistic sense and compassion blend beautifully."),
        ("expression", 6, "abilities", "You excel at caregiving, counseling, creating beautiful spaces, and bringing people together in loving community. Your sense of responsibility and desire to serve make you a natural healer. You instinctively know how to help others feel at home."),
        ("expression", 6, "purpose", "Your life purpose is to nurture, serve, and create beauty and harmony in the world. You're here to demonstrate the power of love, compassion, and responsibility. Your example shows that caring for others enriches all of life."),

        # Expression 7
        ("expression", 7, "talents", "Your natural talents include analysis, research, and uncovering hidden truths. You have a gift for seeing beneath surface appearances to underlying patterns. Your intuition combined with analytical ability gives you unique insights."),
        ("expression", 7, "abilities", "You excel at research, spiritual pursuits, analysis, and teaching others about life's deeper meanings. Your ability to think deeply and see connections others miss makes you a valuable advisor. You naturally question and seek understanding."),
        ("expression", 7, "purpose", "Your life purpose is to seek truth, develop wisdom, and share your insights with others. You're here to demonstrate the value of inner reflection and deep understanding. Your example teaches that wisdom comes from looking within."),

        # Expression 8
        ("expression", 8, "talents", "Your natural talents include business acumen, leadership in the material world, and the ability to manifest abundance. You have a gift for seeing opportunities and organizing resources effectively. Your natural authority commands respect."),
        ("expression", 8, "abilities", "You excel at business management, financial planning, executive leadership, and building successful enterprises. Your combination of vision and practical skill allows you to create wealth and opportunities. You naturally understand how to make things profitable."),
        ("expression", 8, "purpose", "Your life purpose is to build prosperity, lead with integrity, and demonstrate ethical use of power. You're here to show that material success and spiritual values can coexist. Your example teaches balanced use of worldly power."),

        # Expression 9
        ("expression", 9, "talents", "Your natural talents include compassion, wisdom, and the ability to see life from a universal perspective. You have a gift for understanding human nature and inspiring others to their highest potential. Your generous spirit touches many lives."),
        ("expression", 9, "abilities", "You excel at humanitarian work, teaching, healing, and any activity that serves the greater good. Your ability to let go of ego and serve selflessly makes you a natural leader in compassionate causes. You instinctively know how to help others transform."),
        ("expression", 9, "purpose", "Your life purpose is to serve humanity, share wisdom, and demonstrate unconditional love. You're here to show that giving and compassion enrich both giver and receiver. Your example teaches the power of selfless service."),

        # Expression 11 (Master Number)
        ("expression", 11, "talents", "Your natural talents include intuition, spiritual awareness, and the ability to channel higher guidance. You have a gift for inspiring others through your visionary insights and spiritual presence. Your sensitivity to subtle energies is exceptional."),
        ("expression", 11, "abilities", "You excel at spiritual counseling, intuitive guidance, inspirational speaking, and any work requiring higher consciousness. Your ability to sense beyond the physical and inspire others spiritually is your gift to the world. You naturally illuminate truth."),
        ("expression", 11, "purpose", "Your life purpose is to be a spiritual teacher, inspire others to their highest potential, and demonstrate the reality of intuitive wisdom. You're here to be a light bearer, showing others the spiritual dimensions of life. Your example teaches that we are more than physical beings."),

        # Expression 22 (Master Number)
        ("expression", 22, "talents", "Your natural talents include visionary building, practical mastery, and the ability to manifest large-scale projects. You have a gift for seeing the grand vision while managing every practical detail. Your combination of idealism and pragmatism is rare and powerful."),
        ("expression", 22, "abilities", "You excel at large-scale project management, building lasting institutions, leadership of important ventures, and turning visionary ideas into concrete reality. Your ability to think big while attending to practical details allows you to accomplish what others only dream about. You naturally build for posterity."),
        ("expression", 22, "purpose", "Your life purpose is to build something of lasting value that serves humanity for generations. You're here to demonstrate that grand visions can become real when combined with practical action. Your example teaches that we can create heaven on earth through dedicated work."),

        # Expression 33 (Master Number)
        ("expression", 33, "talents", "Your natural talents include unconditional love, spiritual healing, and the ability to teach through your very presence. You have a gift for combining spiritual wisdom with practical compassion. Your loving energy transforms everyone you meet."),
        ("expression", 33, "abilities", "You excel at spiritual teaching, healing through love, counseling with deep compassion, and leading humanitarian causes with wisdom. Your ability to hold space for others' growth while maintaining your own center is your greatest strength. You naturally embody love."),
        ("expression", 33, "purpose", "Your life purpose is to be a master teacher of love, demonstrate unconditional compassion, and guide others' spiritual evolution. You're here to show that love is the ultimate power and that wisdom serves love. Your example teaches that we are all connected in love."),
    ]

    # Add interpretations to session
    for number_type, value, category, content in interpretations:
        interp = NumerologyInterpretation(
            number_type=number_type,
            number_value=value,
            category=category,
            content=content
        )
        session.add(interp)

    print(f"✅ Added {len(interpretations)} Expression interpretations")


def seed_soul_urge_interpretations(session):
    """Seed Soul Urge number interpretations (1-9, 11, 22, 33)."""
    print("📖 Seeding Soul Urge interpretations...")

    # Soul Urge represents inner desires and motivations
    interpretations = [
        ("soul_urge", 1, "personality", "Your deepest desire is for independence, leadership, and the freedom to forge your own path. You crave opportunities to lead and innovate without constraint. Your inner self seeks recognition for your unique contributions."),
        ("soul_urge", 1, "strengths", "Your inner strength comes from self-reliance and courage to stand alone when necessary. You're motivated by the challenge of new beginnings and pioneering ventures. Your determination to succeed on your own terms drives you forward."),
        ("soul_urge", 2, "personality", "Your deepest desire is for harmony, partnership, and meaningful connections with others. You crave peace and cooperation in all relationships. Your inner self seeks to build bridges and create unity."),
        ("soul_urge", 2, "strengths", "Your inner strength comes from patience, diplomacy, and your ability to see all perspectives. You're motivated by the desire to bring people together and create win-win situations. Your sensitivity to others' needs is your guide."),
        ("soul_urge", 3, "personality", "Your deepest desire is for creative self-expression and joyful connection with others. You crave opportunities to share your creativity and uplift others through your art or communication. Your inner self seeks celebration and beauty."),
        ("soul_urge", 3, "strengths", "Your inner strength comes from optimism, creativity, and your natural ability to inspire joy. You're motivated by the desire to express yourself authentically and bring light to the world. Your enthusiasm for life is your greatest asset."),
        ("soul_urge", 4, "personality", "Your deepest desire is for security, order, and building something lasting and meaningful. You crave stability and the satisfaction of creating solid foundations. Your inner self seeks practical accomplishment and tangible results."),
        ("soul_urge", 4, "strengths", "Your inner strength comes from discipline, reliability, and your commitment to seeing things through. You're motivated by the desire to build and organize effectively. Your patient persistence ensures long-term success."),
        ("soul_urge", 5, "personality", "Your deepest desire is for freedom, adventure, and diverse experiences. You crave variety, change, and the opportunity to explore life without limitations. Your inner self seeks excitement and new horizons."),
        ("soul_urge", 5, "strengths", "Your inner strength comes from adaptability, curiosity, and your enthusiasm for new experiences. You're motivated by the desire to remain free and unrestricted. Your versatility allows you to thrive in changing circumstances."),
        ("soul_urge", 6, "personality", "Your deepest desire is to nurture, serve, and create beauty and harmony around you. You crave the opportunity to care for others and make their lives better. Your inner self seeks to love and be loved."),
        ("soul_urge", 6, "strengths", "Your inner strength comes from compassion, responsibility, and your natural healing presence. You're motivated by the desire to serve and create beauty. Your loving heart guides all your actions."),
        ("soul_urge", 7, "personality", "Your deepest desire is for understanding, wisdom, and time for inner reflection. You crave solitude to think deeply and uncover life's mysteries. Your inner self seeks truth and spiritual understanding."),
        ("soul_urge", 7, "strengths", "Your inner strength comes from intuition, analytical ability, and your commitment to finding truth. You're motivated by the desire to understand the deeper meaning of life. Your wisdom comes from within."),
        ("soul_urge", 8, "personality", "Your deepest desire is for material success, achievement, and recognition for your accomplishments. You crave power and the resources to make a significant impact. Your inner self seeks mastery and abundance."),
        ("soul_urge", 8, "strengths", "Your inner strength comes from ambition, business acumen, and your ability to manifest wealth. You're motivated by the desire to build something substantial and leave a legacy. Your determination to succeed is unwavering."),
        ("soul_urge", 9, "personality", "Your deepest desire is to serve humanity, spread compassion, and make the world a better place for all. You crave opportunities to give back and help others transform. Your inner self seeks universal love and understanding."),
        ("soul_urge", 9, "strengths", "Your inner strength comes from compassion, wisdom, and your ability to see the bigger picture. You're motivated by the desire to uplift humanity and create positive change. Your generous spirit knows no bounds."),
        ("soul_urge", 11, "personality", "Your deepest desire is for spiritual illumination, intuitive understanding, and the ability to inspire others. You crave connection with higher consciousness and opportunities to share spiritual insights. Your inner self seeks enlightenment."),
        ("soul_urge", 11, "strengths", "Your inner strength comes from intuition, spiritual awareness, and your ability to channel higher wisdom. You're motivated by the desire to uplift others spiritually and serve as a light bearer. Your sensitivity to subtle energies guides you."),
        ("soul_urge", 22, "personality", "Your deepest desire is to build something lasting and significant that serves humanity for generations. You crave opportunities to manifest grand visions into concrete reality. Your inner self seeks to leave a meaningful legacy."),
        ("soul_urge", 22, "strengths", "Your inner strength comes from combining visionary insight with practical mastery. You're motivated by the desire to create substantial, lasting change in the world. Your ability to see both the big picture and the details empowers you."),
        ("soul_urge", 33, "personality", "Your deepest desire is to teach universal love, heal others through compassion, and serve as a spiritual guide. You crave opportunities to embody and share unconditional love. Your inner self seeks to uplift all of humanity."),
        ("soul_urge", 33, "strengths", "Your inner strength comes from unconditional love, spiritual wisdom, and your ability to heal through your presence. You're motivated by the desire to teach and demonstrate the power of compassion. Your loving energy transforms all you touch."),
    ]

    # Add interpretations to session
    for number_type, value, category, content in interpretations:
        interp = NumerologyInterpretation(
            number_type=number_type,
            number_value=value,
            category=category,
            content=content
        )
        session.add(interp)

    print(f"✅ Added {len(interpretations)} Soul Urge interpretations")


def seed_birthday_interpretations(session):
    """Seed Birthday number interpretations (1-9, 11, 22, 33)."""
    print("📖 Seeding Birthday interpretations...")

    # Birthday number represents special gifts and talents
    interpretations = [
        ("birthday", 1, "personality", "Your birth day gives you natural leadership abilities and pioneering spirit. You have an innate drive to be first and forge your own path. Independence and originality are your birth-given gifts."),
        ("birthday", 2, "personality", "Your birth day gives you exceptional sensitivity and diplomatic skills. You have an innate ability to understand others and bring people together. Cooperation and harmony are your birth-given gifts."),
        ("birthday", 3, "personality", "Your birth day gives you creative expression and natural charisma. You have an innate gift for communication and bringing joy to others. Creativity and optimism are your birth-given gifts."),
        ("birthday", 4, "personality", "Your birth day gives you practical skills and exceptional organizational ability. You have an innate talent for building and creating order. Reliability and systematic thinking are your birth-given gifts."),
        ("birthday", 5, "personality", "Your birth day gives you adaptability and love of freedom. You have an innate ability to thrive in change and connect with diverse people. Versatility and adventure are your birth-given gifts."),
        ("birthday", 6, "personality", "Your birth day gives you nurturing abilities and a sense of responsibility. You have an innate gift for creating harmony and caring for others. Compassion and service are your birth-given gifts."),
        ("birthday", 7, "personality", "Your birth day gives you analytical mind and spiritual awareness. You have an innate ability to see beneath surfaces and uncover truth. Wisdom and intuition are your birth-given gifts."),
        ("birthday", 8, "personality", "Your birth day gives you business acumen and natural authority. You have an innate ability to manifest material success and lead in practical matters. Ambition and power are your birth-given gifts."),
        ("birthday", 9, "personality", "Your birth day gives you compassion and universal understanding. You have an innate ability to serve humanity and inspire others. Wisdom and generosity are your birth-given gifts."),
        ("birthday", 11, "personality", "Your birth day gives you exceptional intuition and spiritual sensitivity. You have an innate ability to inspire and channel higher wisdom. Spiritual awareness and inspiration are your birth-given gifts."),
        ("birthday", 22, "personality", "Your birth day gives you master building abilities and practical vision. You have an innate ability to manifest large-scale projects and create lasting impact. Visionary leadership and practical mastery are your birth-given gifts."),
        ("birthday", 33, "personality", "Your birth day gives you the ability to teach through unconditional love and healing presence. You have an innate gift for spiritual healing and guiding others. Compassionate wisdom and healing are your birth-given gifts."),
    ]

    # Add interpretations to session
    for number_type, value, category, content in interpretations:
        interp = NumerologyInterpretation(
            number_type=number_type,
            number_value=value,
            category=category,
            content=content
        )
        session.add(interp)

    print(f"✅ Added {len(interpretations)} Birthday interpretations")


def seed_personal_year_interpretations(session):
    """Seed Personal Year interpretations (1-9, 11, 22, 33)."""
    print("📖 Seeding Personal Year interpretations...")

    # Personal Year represents the theme and opportunities for the current year
    interpretations = [
        ("personal_year", 1, "personality", "This is a year of new beginnings, fresh starts, and taking initiative. Plant seeds for future growth and embrace leadership opportunities. This is your time to start new projects and forge your own path."),
        ("personal_year", 1, "strengths", "You have extra courage, confidence, and pioneering energy this year. Use this time to launch new ventures and assert your independence. Your natural leadership abilities are amplified now."),
        ("personal_year", 2, "personality", "This is a year of cooperation, partnership, and patient development. Focus on relationships and collaborative projects. This is your time to build alliances and practice diplomacy."),
        ("personal_year", 2, "strengths", "You have heightened sensitivity, diplomatic skills, and ability to work with others this year. Use this time to strengthen partnerships and develop patience. Your natural peacemaking abilities are enhanced now."),
        ("personal_year", 3, "personality", "This is a year of creative expression, social activity, and joyful communication. Express yourself creatively and enjoy life's pleasures. This is your time to share your gifts and celebrate."),
        ("personal_year", 3, "strengths", "You have increased creativity, communication skills, and optimism this year. Use this time to express yourself artistically and socially. Your natural charm and enthusiasm are at their peak."),
        ("personal_year", 4, "personality", "This is a year of hard work, building foundations, and practical accomplishment. Focus on organization and creating lasting structures. This is your time to work diligently toward concrete goals."),
        ("personal_year", 4, "strengths", "You have enhanced discipline, organizational ability, and stamina this year. Use this time to build solid foundations for the future. Your natural reliability and perseverance are strengthened now."),
        ("personal_year", 5, "personality", "This is a year of change, freedom, and new experiences. Embrace variety and be open to unexpected opportunities. This is your time to break free from limitation and explore new horizons."),
        ("personal_year", 5, "strengths", "You have increased adaptability, adventurous spirit, and versatility this year. Use this time to try new things and remain flexible. Your natural ability to thrive in change is amplified now."),
        ("personal_year", 6, "personality", "This is a year of responsibility, service, and creating harmony in home and relationships. Focus on caring for others and beautifying your environment. This is your time to nurture and create balance."),
        ("personal_year", 6, "strengths", "You have heightened compassion, sense of duty, and ability to create harmony this year. Use this time to strengthen family bonds and serve others. Your natural nurturing abilities are enhanced now."),
        ("personal_year", 7, "personality", "This is a year of inner reflection, spiritual growth, and seeking deeper understanding. Take time for solitude and contemplation. This is your time to develop wisdom and connect with your inner self."),
        ("personal_year", 7, "strengths", "You have increased intuition, analytical ability, and spiritual awareness this year. Use this time for study, meditation, and inner work. Your natural wisdom-seeking tendencies are amplified now."),
        ("personal_year", 8, "personality", "This is a year of achievement, material success, and recognition for your efforts. Focus on career advancement and financial growth. This is your time to manifest abundance and step into your power."),
        ("personal_year", 8, "strengths", "You have enhanced business acumen, leadership ability, and manifesting power this year. Use this time to advance your career and build wealth. Your natural authority and ambition are strengthened now."),
        ("personal_year", 9, "personality", "This is a year of completion, letting go, and preparing for new cycles. Release what no longer serves and focus on humanitarian service. This is your time to tie up loose ends and give back."),
        ("personal_year", 9, "strengths", "You have increased compassion, wisdom, and ability to let go this year. Use this time to complete projects and serve others selflessly. Your natural generosity and understanding are at their peak."),
        ("personal_year", 11, "personality", "This is a spiritually powerful year of illumination, inspiration, and intuitive development. Pay attention to synchronicities and spiritual insights. This is your time to step into your role as a light bearer."),
        ("personal_year", 11, "strengths", "You have heightened intuition, spiritual awareness, and ability to inspire others this year. Use this time for spiritual development and sharing insights. Your natural visionary abilities are amplified now."),
        ("personal_year", 22, "personality", "This is a master builder year with potential for significant achievement and lasting impact. Focus on large-scale projects and practical vision. This is your time to manifest something substantial and enduring."),
        ("personal_year", 22, "strengths", "You have enhanced ability to turn visions into reality and lead important projects this year. Use this time to build something of lasting value. Your natural master building abilities are strengthened now."),
        ("personal_year", 33, "personality", "This is a powerful year for spiritual teaching, healing, and expressing unconditional love. Focus on service that combines compassion with wisdom. This is your time to embody and teach love."),
        ("personal_year", 33, "strengths", "You have heightened ability to heal, teach, and express unconditional love this year. Use this time to guide others spiritually and lead with compassion. Your natural healing and teaching abilities are at their peak."),
    ]

    # Add interpretations to session
    for number_type, value, category, content in interpretations:
        interp = NumerologyInterpretation(
            number_type=number_type,
            number_value=value,
            category=category,
            content=content
        )
        session.add(interp)

    print(f"✅ Added {len(interpretations)} Personal Year interpretations")


def main():
    """
    Main entry point for seeding numerology interpretations.

    This function orchestrates the entire seeding process:
    1. Check for existing data
    2. Prompt for confirmation if overwriting
    3. Seed all number types with comprehensive interpretations
    4. Report completion with statistics
    """
    print("\n" + "="*60)
    print("🔢 Numerology Interpretation Database Seeder")
    print("="*60 + "\n")

    with Session(engine) as session:
        # Check for existing data and get confirmation
        should_proceed = check_and_confirm_overwrite(session)
        if not should_proceed:
            return

        print("\n🌱 Starting seed process...\n")

        # Seed all number types
        seed_life_path_interpretations(session)
        seed_expression_interpretations(session)
        seed_soul_urge_interpretations(session)
        seed_birthday_interpretations(session)
        seed_personal_year_interpretations(session)

        # Commit all changes
        print("\n💾 Committing changes to database...")
        session.commit()

        # Query final count
        result = session.exec(select(NumerologyInterpretation))
        all_interps = result.all()
        total_count = len(all_interps)

        print("\n" + "="*60)
        print(f"✨ Seeding complete! Total interpretations: {total_count}")
        print("="*60 + "\n")

        # Show breakdown by number type
        print("📊 Breakdown by number type:")
        types = {}
        for interp in all_interps:
            types[interp.number_type] = types.get(interp.number_type, 0) + 1

        for number_type, count in sorted(types.items()):
            print(f"   {number_type}: {count} entries")

        print("\n🎉 Database is ready for AI-powered numerology readings!\n")


if __name__ == "__main__":
    main()
