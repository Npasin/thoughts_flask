-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema thoughts_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `thoughts_db` ;

-- -----------------------------------------------------
-- Schema thoughts_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `thoughts_db` DEFAULT CHARACTER SET utf8 ;
USE `thoughts_db` ;

-- -----------------------------------------------------
-- Table `thoughts_db`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thoughts_db`.`users` ;

CREATE TABLE IF NOT EXISTS `thoughts_db`.`users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `thoughts_db`.`thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thoughts_db`.`thoughts` ;

CREATE TABLE IF NOT EXISTS `thoughts_db`.`thoughts` (
  `thought_id` INT NOT NULL AUTO_INCREMENT,
  `content` TEXT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `author` INT NOT NULL,
  PRIMARY KEY (`thought_id`),
  INDEX `fk_thoughts_users_idx` (`author` ASC) VISIBLE,
  CONSTRAINT `fk_thoughts_users`
    FOREIGN KEY (`author`)
    REFERENCES `thoughts_db`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `thoughts_db`.`user_likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `thoughts_db`.`user_likes` ;

CREATE TABLE IF NOT EXISTS `thoughts_db`.`user_likes` (
  `user_like` INT NOT NULL,
  `thought_like` INT NOT NULL,
  PRIMARY KEY (`user_like`, `thought_like`),
  INDEX `fk_users_has_thoughts_thoughts1_idx` (`thought_like` ASC) VISIBLE,
  INDEX `fk_users_has_thoughts_users1_idx` (`user_like` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_thoughts_users1`
    FOREIGN KEY (`user_like`)
    REFERENCES `thoughts_db`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_thoughts_thoughts1`
    FOREIGN KEY (`thought_like`)
    REFERENCES `thoughts_db`.`thoughts` (`thought_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
