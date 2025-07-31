-- =============================================================================
-- Gather Pass: Seed Data Script (Corrected)
-- Version: 1.2
-- Description: This script populates the database with a complete set of
--              test data, now with robust subqueries for all foreign keys.
-- =============================================================================

-- To ensure a clean import, we'll start by deleting data from all tables
-- in the reverse order of their creation to respect foreign key constraints.
DELETE FROM user_prize_award;
DELETE FROM season_user_rank;
DELETE FROM submission;
DELETE FROM season_user;
DELETE FROM season_prize;
DELETE FROM season_rank;
DELETE FROM season_item;
DELETE FROM prize;
DELETE FROM rank;
DELETE FROM item;
DELETE FROM season;
DELETE FROM user;


-- =============================================================================
-- 1. Core Entities
-- =============================================================================

-- Insert 25 Users
INSERT INTO `user` (`id`, `uuid`, `discord_id`, `in_game_name`, `lodestone_id`, `status`, `admin`, `created_by`, `updated_by`) VALUES
(1, UUID(), 100000000000000001, 'Bombastic Billy', '1001', 'verified', 1, 'system', 'system'),
(2, UUID(), 100000000000000002, 'Scornful Suzy', '1002', 'verified', 1, 'system', 'system'),
(3, UUID(), 100000000000000003, 'Triumphant Timmy', '1003', 'verified', 0, 'system', 'system'),
(4, UUID(), 100000000000000004, 'Rhayna Thundercall', '1004', 'verified', 0, 'system', 'system'),
(5, UUID(), 100000000000000005, 'Gideon Frost', '1005', 'verified', 0, 'system', 'system'),
(6, UUID(), 100000000000000006, 'Elara Meadowlight', '1006', 'verified', 0, 'system', 'system'),
(7, UUID(), 100000000000000007, 'Jax Ironhide', '1007', 'verified', 0, 'system', 'system'),
(8, UUID(), 100000000000000008, 'Lyra Swiftwind', '1008', 'verified', 0, 'system', 'system'),
(9, UUID(), 100000000000000009, 'Kaelen Shadowsun', '1009', 'verified', 0, 'system', 'system'),
(10, UUID(), 100000000000000010, 'Seraphina Fireheart', '1010', 'verified', 0, 'system', 'system'),
(11, UUID(), 100000000000000011, 'Orion Nightshade', '1011', 'verified', 0, 'system', 'system'),
(12, UUID(), 100000000000000012, 'Faye Whisperwind', '1012', 'verified', 0, 'system', 'system'),
(13, UUID(), 100000000000000013, 'Bram Stonefist', '1013', 'verified', 0, 'system', 'system'),
(14, UUID(), 100000000000000014, 'Isolde Moonbrook', '1014', 'verified', 0, 'system', 'system'),
(15, UUID(), 100000000000000015, 'Roric Earthshaker', '1015', 'verified', 0, 'system', 'system'),
(16, UUID(), 100000000000000016, 'Sylas Sunstrider', '1016', 'verified', 0, 'system', 'system'),
(17, UUID(), 100000000000000017, 'Astrid Snowfall', '1017', 'verified', 0, 'system', 'system'),
(18, UUID(), 100000000000000018, 'Garrick Stormwind', '1018', 'verified', 0, 'system', 'system'),
(19, UUID(), 100000000000000019, 'Rowan Darkwood', '1019', 'verified', 0, 'system', 'system'),
(20, UUID(), 100000000000000020, 'Tamsin Riverbend', '1020', 'verified', 0, 'system', 'system'),
(21, UUID(), 100000000000000021, 'Finnian Greymane', '1021', 'verified', 0, 'system', 'system'),
(22, UUID(), 100000000000000022, 'Moira Bronzebeard', '1022', 'verified', 0, 'system', 'system'),
(23, UUID(), 100000000000000023, 'Caden Swiftbow', '1023', 'verified', 0, 'system', 'system'),
(24, UUID(), 100000000000000024, 'Briar Rosewood', '1024', 'verified', 0, 'system', 'system'),
(25, UUID(), 100000000000000025, 'Zephyr Windrunner', '1025', 'verified', 0, 'system', 'system');

-- Insert 2 Seasons
INSERT INTO `season` (`id`, `number`, `name`, `start_date`, `end_date`) VALUES
(1, 1, 'Season 1: The First Hunt', '2025-01-01 00:00:00', '2025-04-01 23:59:59'),
(2, 2, 'Season 2: The Sunken City', '2025-06-01 00:00:00', '2025-09-01 23:59:59');

-- Insert 15 Items
INSERT INTO `item` (`id`, `lodestone_id`, `name`) VALUES
(1, '5050', 'Copper Ore'), (2, '5051', 'Iron Ore'), (3, '5052', 'Silver Ore'),
(4, '5053', 'Mythril Ore'), (5, '5054', 'Darksteel Ore'), (6, '5055', 'Adamantite Ore'),
(7, '27', 'Maple Log'), (8, '28', 'Oak Log'), (9, '29', 'Yew Log'),
(10, '30', 'Mahogany Log'), (11, '1990', 'Gummy Minnow'), (12, '1991', 'Crayfish'),
(13, '1992', 'Tiger Cod'), (14, '1993', 'Silver Shark'), (15, '1994', 'Tuna');

-- Insert 15 Ranks
INSERT INTO `rank` (`id`, `name`, `badge_url`) VALUES
(1, 'Bronze I', NULL), (2, 'Bronze II', NULL), (3, 'Silver I', NULL),
(4, 'Silver II', NULL), (5, 'Gold I', NULL), (6, 'Gold II', NULL),
(7, 'Platinum I', NULL), (8, 'Platinum II', NULL), (9, 'Diamond', NULL),
(10, 'Crystal', NULL), (11, 'Adept', NULL), (12, 'Master', NULL),
(13, 'Grandmaster', NULL), (14, 'Elite', NULL), (15, 'Legend', NULL);

-- Insert 20 Prizes
INSERT INTO `prize` (`id`, `description`, `value`, `lodestone_id`, `discord_role`) VALUES
(1, '10,000 Gil', 10000, NULL, NULL), (2, '50,000 Gil', 50000, NULL, NULL),
(3, '100,000 Gil', 100000, NULL, NULL), (4, '250,000 Gil', 250000, NULL, NULL),
(5, '500,000 Gil', 500000, NULL, NULL), (6, '1,000,000 Gil', 1000000, NULL, NULL),
(7, 'Choice of one Grade 8 Materia', NULL, '5580', NULL), (8, 'Choice of three Grade 8 Materia', NULL, '5580', NULL),
(9, 'Choice of one Grade 10 Materia', NULL, '5590', NULL), (10, 'Choice of three Grade 10 Materia', NULL, '5590', NULL),
(11, 'A stack of high-quality food', NULL, '4685', NULL), (12, 'A stack of high-quality potions', NULL, '4557', NULL),
(13, 'Custom FC Room Furnishing', NULL, NULL, NULL), (14, 'A minion of your choice (up to 1M gil value)', 1000000, NULL, NULL),
(15, 'A mount of your choice (up to 5M gil value)', 5000000, NULL, NULL), (16, 'Custom Drawn Character Portrait', NULL, NULL, NULL),
(17, 'A crafted glamour set', NULL, NULL, NULL), (18, 'Season 1 Champion Discord Title', NULL, NULL, 200000000000000001),
(19, 'Season 2 Champion Discord Title', NULL, NULL, 200000000000000002), (20, 'Special FC Event Participation', NULL, NULL, NULL);


-- =============================================================================
-- 2. Join Table Setup
-- =============================================================================

-- Register users for seasons
INSERT INTO `season_user` (`user_id`, `season_id`, `total_points`, `created_by`, `updated_by`) SELECT id, 1, 0, 'system', 'system' FROM `user` WHERE id BETWEEN 3 AND 20;
INSERT INTO `season_user` (`user_id`, `season_id`, `total_points`, `created_by`, `updated_by`) SELECT id, 2, 0, 'system', 'system' FROM `user` WHERE id BETWEEN 3 AND 20;
INSERT INTO `season_user` (`user_id`, `season_id`, `total_points`, `created_by`, `updated_by`) SELECT id, 1, 0, 'system', 'system' FROM `user` WHERE id BETWEEN 21 AND 23;
INSERT INTO `season_user` (`user_id`, `season_id`, `total_points`, `created_by`, `updated_by`) SELECT id, 2, 0, 'system', 'system' FROM `user` WHERE id BETWEEN 24 AND 25;

-- Add items to seasons with point values
INSERT INTO `season_item` (`season_id`, `item_id`, `point_value`) VALUES
(1, 1, 10), (1, 2, 20), (1, 3, 50), (1, 7, 15), (1, 8, 25), (1, 11, 30), (1, 12, 40),
(2, 1, 15), (2, 2, 25), (2, 3, 55), (2, 7, 20), (2, 8, 30), (2, 11, 35), (2, 12, 45),
(1, 4, 100), (1, 9, 120), (1, 13, 200),
(2, 5, 250), (2, 6, 500), (2, 10, 300), (2, 14, 400), (2, 15, 450);

-- Add ranks to seasons with required points
INSERT INTO `season_rank` (`season_id`, `rank_id`, `number`, `required_points`) VALUES
(1, 1, 1, 10000), (1, 2, 2, 20000), (1, 3, 3, 30000), (1, 4, 4, 40000), (1, 5, 5, 50000),
(1, 6, 6, 60000), (1, 7, 7, 70000), (1, 8, 8, 80000), (1, 9, 9, 90000), (1, 15, 10, 100000);
INSERT INTO `season_rank` (`season_id`, `rank_id`, `number`, `required_points`) VALUES
(2, 1, 1, 10000), (2, 3, 2, 20000), (2, 5, 3, 30000), (2, 7, 4, 40000), (2, 9, 5, 50000),
(2, 10, 6, 60000), (2, 11, 7, 70000), (2, 12, 8, 80000), (2, 13, 9, 90000), (2, 14, 10, 100000);

-- Add prizes to season ranks
INSERT INTO `season_prize` (`season_rank_id`, `prize_id`) VALUES
((SELECT id FROM season_rank WHERE season_id=1 AND number=1), 1),
((SELECT id FROM season_rank WHERE season_id=1 AND number=2), 2),
((SELECT id FROM season_rank WHERE season_id=1 AND number=3), 7),
((SELECT id FROM season_rank WHERE season_id=1 AND number=4), 3),
((SELECT id FROM season_rank WHERE season_id=1 AND number=5), 8),
((SELECT id FROM season_rank WHERE season_id=1 AND number=6), 11),
((SELECT id FROM season_rank WHERE season_id=1 AND number=7), 4),
((SELECT id FROM season_rank WHERE season_id=1 AND number=8), 9),
((SELECT id FROM season_rank WHERE season_id=1 AND number=9), 14),
((SELECT id FROM season_rank WHERE season_id=1 AND number=10), 18),
((SELECT id FROM season_rank WHERE season_id=2 AND number=1), 1),
((SELECT id FROM season_rank WHERE season_id=2 AND number=2), 2),
((SELECT id FROM season_rank WHERE season_id=2 AND number=3), 12),
((SELECT id FROM season_rank WHERE season_id=2 AND number=4), 5),
((SELECT id FROM season_rank WHERE season_id=2 AND number=5), 10),
((SELECT id FROM season_rank WHERE season_id=2 AND number=6), 17),
((SELECT id FROM season_rank WHERE season_id=2 AND number=7), 6),
((SELECT id FROM season_rank WHERE season_id=2 AND number=8), 13),
((SELECT id FROM season_rank WHERE season_id=2 AND number=9), 15),
((SELECT id FROM season_rank WHERE season_id=2 AND number=10), 19);


-- =============================================================================
-- 3. Submissions & Point Calculation
-- =============================================================================

-- User 3 in Season 1 (20,000 pts)
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (3, (SELECT id FROM season_item WHERE season_id=1 AND item_id=3), 400, 20000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 20000 WHERE user_id = 3 AND season_id = 1;

-- User 4 in Season 1 (100,000 pts)
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (4, (SELECT id FROM season_item WHERE season_id=1 AND item_id=4), 1000, 100000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 100000 WHERE user_id = 4 AND season_id = 1;

-- User 5 in Season 2 (48,500 pts)
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (5, (SELECT id FROM season_item WHERE season_id=2 AND item_id=6), 1, 500, '1', '1');
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (5, (SELECT id FROM season_item WHERE season_id=2 AND item_id=14), 120, 48000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 48500 WHERE user_id = 5 AND season_id = 2;

-- User 6 in both seasons
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (6, (SELECT id FROM season_item WHERE season_id=1 AND item_id=1), 1000, 10000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 10000 WHERE user_id = 6 AND season_id = 1;
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (6, (SELECT id FROM season_item WHERE season_id=2 AND item_id=12), 500, 22500, '1', '1');
UPDATE `season_user` SET total_points = total_points + 22500 WHERE user_id = 6 AND season_id = 2;

-- User 21 (Season 1 only)
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (21, (SELECT id FROM season_item WHERE season_id=1 AND item_id=2), 50, 1000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 1000 WHERE user_id = 21 AND season_id = 1;

-- User 24 (Season 2 only)
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`, `created_by`, `updated_by`) 
VALUES (24, (SELECT id FROM season_item WHERE season_id=2 AND item_id=10), 10, 3000, '1', '1');
UPDATE `season_user` SET total_points = total_points + 3000 WHERE user_id = 24 AND season_id = 2;


-- =============================================================================
-- 4. Award Ranks and Prizes
-- =============================================================================

-- Award ranks based on points
INSERT INTO `season_user_rank` (`user_id`, `season_rank_id`) VALUES 
(3, (SELECT id FROM season_rank WHERE season_id=1 AND number=1)),
(3, (SELECT id FROM season_rank WHERE season_id=1 AND number=2)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=1)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=2)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=3)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=4)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=5)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=6)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=7)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=8)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=9)),
(4, (SELECT id FROM season_rank WHERE season_id=1 AND number=10)),
(5, (SELECT id FROM season_rank WHERE season_id=2 AND number=1)),
(5, (SELECT id FROM season_rank WHERE season_id=2 AND number=2)),
(5, (SELECT id FROM season_rank WHERE season_id=2 AND number=3)),
(5, (SELECT id FROM season_rank WHERE season_id=2 AND number=4)),
(6, (SELECT id FROM season_rank WHERE season_id=1 AND number=1)),
(6, (SELECT id FROM season_rank WHERE season_id=2 AND number=1)),
(6, (SELECT id FROM season_rank WHERE season_id=2 AND number=2));

-- Award prizes for every rank achieved and mark as delivered
INSERT INTO `user_prize_award` (`user_id`, `season_prize_id`, `delivered`, `delivered_at`, `delivered_by`) VALUES
(3, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=1)), 1, NOW(), 100000000000000001),
(3, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=2)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=1)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=2)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=3)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=4)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=5)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=6)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=7)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=8)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=9)), 1, NOW(), 100000000000000001),
(4, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=10)), 1, NOW(), 100000000000000001),
(5, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=1)), 1, NOW(), 100000000000000001),
(5, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=2)), 1, NOW(), 100000000000000001),
(5, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=3)), 1, NOW(), 100000000000000001),
(5, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=4)), 1, NOW(), 100000000000000001),
(6, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=1 AND number=1)), 1, NOW(), 100000000000000001),
(6, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=1)), 1, NOW(), 100000000000000001),
(6, (SELECT id FROM season_prize WHERE season_rank_id=(SELECT id FROM season_rank WHERE season_id=2 AND number=2)), 1, NOW(), 100000000000000001);
