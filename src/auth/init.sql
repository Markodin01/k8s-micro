-- Explicitly select a default database
USE mysql;

-- Create a stored procedure for user creation
DELIMITER //
CREATE PROCEDURE CreateUserIfNotExists()
BEGIN
    DECLARE user_count INT;

    -- Check if the user exists
    SELECT COUNT(*) INTO user_count
    FROM mysql.user
    WHERE user = 'auth_user' AND host = 'localhost';

    -- If the user doesn't exist, create it
    IF user_count = 0 THEN
        CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'auth123';
        GRANT ALL PRIVILEGES ON *.* TO 'auth_user'@'localhost';
    END IF;
END //
DELIMITER ;

-- Call the stored procedure
CALL CreateUserIfNotExists();

-- Switch to the desired database
USE auth;

CREATE DATABASE IF NOT EXISTS auth;

GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

USE auth;

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO `user` (email, password) VALUES ('example@mail.com', 'Adam');

