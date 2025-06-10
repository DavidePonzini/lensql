BEGIN;

SET search_path to lensql;

CREATE OR REPLACE FUNCTION remove_students_if_not_teacher()
    RETURNS TRIGGER AS $$
        BEGIN
            SET search_path TO lensql;

            IF OLD.is_teacher = TRUE AND NEW.is_teacher = FALSE THEN
                DELETE FROM teaches WHERE teacher = OLD.username;
            END IF;
            RETURN NEW;
        END;
    $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_remove_students_if_not_teacher
    BEFORE UPDATE ON users
    FOR EACH ROW
    WHEN (OLD.is_teacher = TRUE AND NEW.is_teacher = FALSE)
    EXECUTE FUNCTION remove_students_if_not_teacher();


COMMIT;