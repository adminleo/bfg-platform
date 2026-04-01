-- Seed: Default diagnostics
-- Tables are created by SQLAlchemy on startup, this seeds initial data

-- We use a DO block to only insert if table exists and is empty
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'diagnostics') THEN
        INSERT INTO diagnostics (id, slug, name, description, category, scientific_basis, version, config, min_questions, max_questions, available_tiers, is_active, created_at)
        SELECT
            gen_random_uuid(),
            'scil',
            'S.C.I.L. Profile — Wirkungskompetenz',
            'Misst Ihre kommunikative Wirkung über 4 Frequenzbereiche (Sensus, Corpus, Intellektus, Lingua) mit 16 Interaktionsfaktoren. Zeigt, wie Sie auf andere wirken und wie Sie Ihr Wirkungsrepertoire erweitern können.',
            'communication',
            'Entwickelt von Andreas Bornhäusser mit Universität Duisburg-Essen. 30+ Jahre Forschung, 140.000+ Teilnehmer.',
            '2.0',
            '{"frequencies": {"sensus": ["inner_presence", "conviction", "moment_focus", "emotionality"], "corpus": ["appearance", "gesture", "facial_expression", "spatial_presence"], "intellektus": ["analytics", "goal_orientation", "structure", "objectivity"], "lingua": ["voice", "articulation", "eloquence", "imagery"]}}',
            24, 100,
            '["S", "M", "L", "XL"]',
            true,
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM diagnostics WHERE slug = 'scil');

        INSERT INTO diagnostics (id, slug, name, description, category, scientific_basis, version, config, min_questions, max_questions, available_tiers, is_active, created_at)
        SELECT
            gen_random_uuid(),
            'big_five',
            'Big Five — Persönlichkeitsprofil (OCEAN)',
            'Der wissenschaftliche Goldstandard der Persönlichkeitsdiagnostik. Misst Offenheit, Gewissenhaftigkeit, Extraversion, Verträglichkeit und Neurotizismus.',
            'personality',
            'Basierend auf IPIP (International Personality Item Pool). Höchste wissenschaftliche Validität unter allen Persönlichkeitsmodellen. Kulturübergreifend validiert.',
            '1.0',
            '{"dimensions": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]}',
            20, 300,
            '["S", "M", "L", "XL"]',
            true,
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM diagnostics WHERE slug = 'big_five');

        INSERT INTO diagnostics (id, slug, name, description, category, scientific_basis, version, config, min_questions, max_questions, available_tiers, is_active, created_at)
        SELECT
            gen_random_uuid(),
            'values_schwartz',
            'Werteprofil (Schwartz)',
            'Identifiziert Ihre 19 universellen Grundwerte und deren Hierarchie. Zeigt, was Sie wirklich antreibt und motiviert.',
            'values',
            'Schwartz PVQ-RR. Kulturübergreifend validiert über 80+ Länder. Goldstandard der Wertediagnostik.',
            '1.0',
            '{"values": ["self_direction_thought", "self_direction_action", "stimulation", "hedonism", "achievement", "power_dominance", "power_resources", "face", "security_personal", "security_societal", "tradition", "conformity_rules", "conformity_interpersonal", "humility", "benevolence_caring", "benevolence_dependability", "universalism_concern", "universalism_nature", "universalism_tolerance"]}',
            20, 57,
            '["S", "M", "L", "XL"]',
            true,
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM diagnostics WHERE slug = 'values_schwartz');

        INSERT INTO diagnostics (id, slug, name, description, category, scientific_basis, version, config, min_questions, max_questions, available_tiers, is_active, created_at)
        SELECT
            gen_random_uuid(),
            'eq_trait',
            'Emotionale Intelligenz (Trait-EI)',
            'Misst 15 Facetten Ihrer emotionalen Intelligenz: Wie gut erkennen, verstehen und steuern Sie Emotionen bei sich und anderen?',
            'emotional_intelligence',
            'TEIQue-basiert. 15 Facetten in 4 Faktoren. Gut geeignet für Coaching und Entwicklung.',
            '1.0',
            '{"factors": ["wellbeing", "self_control", "emotionality", "sociability"], "facets": 15}',
            20, 153,
            '["S", "M", "L", "XL"]',
            true,
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM diagnostics WHERE slug = 'eq_trait');

        INSERT INTO diagnostics (id, slug, name, description, category, scientific_basis, version, config, min_questions, max_questions, available_tiers, is_active, created_at)
        SELECT
            gen_random_uuid(),
            'resilience',
            'Resilienz-Profil',
            'Erfasst Ihre psychische Widerstandsfähigkeit und Erholungsfähigkeit nach Belastungen. Zeigt konkrete Ansatzpunkte zur Stärkung Ihrer Resilienz.',
            'resilience',
            'Basierend auf CD-RISC (Connor-Davidson). Breit validiert, längsschnittfähig. Resilienz als trainierbare Fähigkeit.',
            '1.0',
            '{"dimensions": ["personal_competence", "trust_tolerance", "positive_acceptance", "control", "spiritual_influences"]}',
            10, 25,
            '["S", "M", "L", "XL"]',
            true,
            NOW()
        WHERE NOT EXISTS (SELECT 1 FROM diagnostics WHERE slug = 'resilience');
    END IF;
END $$;
