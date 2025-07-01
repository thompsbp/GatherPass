-- SQL Schema for the GatherPass Database
-- Target DBMS: MariaDB
-- Version: 1.0

-- --- Database Creation ---
CREATE DATABASE IF NOT EXISTS GatherPass;
USE GatherPass;

-- --- Table Creation ---

-- Table: user
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `discord_id` VARCHAR(255) UNIQUE,
  `in_game_name` VARCHAR(255),
  `lodestone_id` INT,
  `status` ENUM('pending', 'verified', 'banned'),
  `admin` BOOLEAN DEFAULT FALSE,
  `api_token` VARCHAR(255) UNIQUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_discord_id` (`discord_id`),
  INDEX `idx_lodestone_id` (`lodestone_id`)
);

-- Table: season
CREATE TABLE IF NOT EXISTS `season` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `number` INT,
  `name` VARCHAR(255),
  `start_date` TIMESTAMP,
  `end_date` TIMESTAMP,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: season_user
CREATE TABLE IF NOT EXISTS `season_user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `season_id` INT,
  `total_points` INT DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE `uq_user_season` (`user_id`, `season_id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_season_id` (`season_id`)
);

-- Table: item
CREATE TABLE IF NOT EXISTS `item` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `lodestone_id` INT UNIQUE,
  `name` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_lodestone_id` (`lodestone_id`)
);

-- Table: season_item
CREATE TABLE IF NOT EXISTS `season_item` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `season_id` INT,
  `item_id` INT,
  `point_value` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE `uq_season_item` (`season_id`, `item_id`),
  INDEX `idx_season_id` (`season_id`),
  INDEX `idx_item_id` (`item_id`)
);

-- Table: rank
CREATE TABLE IF NOT EXISTS `rank` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255),
  `badge_url` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: prize
CREATE TABLE IF NOT EXISTS `prize` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `description` VARCHAR(255),
  `value` INT,
  `lodestone_id` INT,
  `discord_role` BIGINT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: season_rank
CREATE TABLE IF NOT EXISTS `season_rank` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `season_id` INT,
  `rank_id` INT,
  `number` INT,
  `required_points` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE `uq_season_rank` (`season_id`, `rank_id`),
  INDEX `idx_season_id` (`season_id`),
  INDEX `idx_rank_id` (`rank_id`)
);

-- Table: season_user_rank
CREATE TABLE IF NOT EXISTS `season_user_rank` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `season_rank_id` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE `uq_user_season_rank` (`user_id`, `season_rank_id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_season_rank_id` (`season_rank_id`)
);

-- Table: season_prize
CREATE TABLE IF NOT EXISTS `season_prize` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `prize_id` INT,
  `season_rank_id` INT,
  INDEX `idx_prize_id` (`prize_id`),
  INDEX `idx_season_rank_id` (`season_rank_id`)
);

-- Table: submission
CREATE TABLE IF NOT EXISTS `submission` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `season_item_id` INT,
  `quantity` INT DEFAULT 1,
  `total_point_value` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_season_item_id` (`season_item_id`)
);


-- --- Foreign Key Constraints ---
-- Using ALTER TABLE to add constraints after all tables are created to avoid order-of-creation issues.

ALTER TABLE `season_user` ADD CONSTRAINT `fk_season_user_to_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE CASCADE;
ALTER TABLE `season_user` ADD CONSTRAINT `fk_season_user_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

ALTER TABLE `season_item` ADD CONSTRAINT `fk_season_item_to_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE CASCADE;
ALTER TABLE `season_item` ADD CONSTRAINT `fk_season_item_to_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE;

ALTER TABLE `submission` ADD CONSTRAINT `fk_submission_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
ALTER TABLE `submission` ADD CONSTRAINT `fk_submission_to_season_item` FOREIGN KEY (`season_item_id`) REFERENCES `season_item` (`id`) ON DELETE SET NULL;

ALTER TABLE `season_rank` ADD CONSTRAINT `fk_season_rank_to_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE CASCADE;
ALTER TABLE `season_rank` ADD CONSTRAINT `fk_season_rank_to_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`id`) ON DELETE CASCADE;

ALTER TABLE `season_user_rank` ADD CONSTRAINT `fk_season_user_rank_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
ALTER TABLE `season_user_rank` ADD CONSTRAINT `fk_season_user_rank_to_season_rank` FOREIGN KEY (`season_rank_id`) REFERENCES `season_rank` (`id`) ON DELETE CASCADE;

ALTER TABLE `season_prize` ADD CONSTRAINT `fk_season_prize_to_season_rank` FOREIGN KEY (`season_rank_id`) REFERENCES `season_rank` (`id`) ON DELETE CASCADE;
ALTER TABLE `season_prize` ADD CONSTRAINT `fk_season_prize_to_prize` FOREIGN KEY (`prize_id`) REFERENCES `prize` (`id`) ON DELETE CASCADE;

