-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema photos
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `photos` ;

-- -----------------------------------------------------
-- Schema photos
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `photos` DEFAULT CHARACTER SET utf8 ;
USE `photos` ;

-- -----------------------------------------------------
-- Table `photos`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `photos`.`user` ;

CREATE TABLE IF NOT EXISTS `photos`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(10) NOT NULL,
  `hash` BLOB NULL,
  `salt` VARCHAR(45) NULL,
  `first` VARCHAR(20) NULL,
  `last` VARCHAR(30) NULL,
  `email` VARCHAR(30) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `photos`.`photo`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `photos`.`photo` ;

CREATE TABLE IF NOT EXISTS `photos`.`photo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_photo_user_idx` (`user_id` ASC),
  CONSTRAINT `fk_photo_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `photos`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `photos`.`type`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `photos`.`type` ;

CREATE TABLE IF NOT EXISTS `photos`.`type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `label` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `photos`.`transformation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `photos`.`transformation` ;

CREATE TABLE IF NOT EXISTS `photos`.`transformation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `filename` VARCHAR(128) NOT NULL,
  `type_id` INT NOT NULL,
  `photo_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_transformation_type1_idx` (`type_id` ASC),
  INDEX `fk_transformation_photo1_idx` (`photo_id` ASC),
  CONSTRAINT `fk_transformation_type1`
    FOREIGN KEY (`type_id`)
    REFERENCES `photos`.`type` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transformation_photo1`
    FOREIGN KEY (`photo_id`)
    REFERENCES `photos`.`photo` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `photos`.`type`
-- -----------------------------------------------------
START TRANSACTION;
USE `photos`;
INSERT INTO `photos`.`type` (`id`, `label`) VALUES (1, 'original');
INSERT INTO `photos`.`type` (`id`, `label`) VALUES (2, 'thumbnail');
INSERT INTO `photos`.`type` (`id`, `label`) VALUES (3, 'trans1');
INSERT INTO `photos`.`type` (`id`, `label`) VALUES (4, 'trans2');
INSERT INTO `photos`.`type` (`id`, `label`) VALUES (5, 'trans3');

COMMIT;

