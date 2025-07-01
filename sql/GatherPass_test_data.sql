-- SQL Test Data for the GatherPass Database
-- Target DBMS: MariaDB
-- Version: 1.0
-- Assumes the schema from the creation script has been applied.

USE GatherPass;

-- --- Core Data Insertion ---

-- Insert Users (75 total, 4 admins)
-- Admins get API tokens, plus a few regular users.
INSERT INTO `user` (`id`, `discord_id`, `in_game_name`, `lodestone_id`, `status`, `admin`, `api_token`) VALUES
(1, '100000000000000001', 'Admin Alpha', 10001, 'verified', TRUE, 'admintoken_alpha_secret'),
(2, '100000000000000002', 'Admin Bravo', 10002, 'verified', TRUE, 'admintoken_bravo_secret'),
(3, '100000000000000003', 'Admin Charlie', 10003, 'verified', TRUE, 'admintoken_charlie_secret'),
(4, '100000000000000004', 'Admin Delta', 10004, 'verified', TRUE, 'admintoken_delta_secret'),
(5, '200000000000000005', 'Power User Pete', 20005, 'verified', FALSE, 'usertoken_pete_secret'),
(6, '200000000000000006', 'API User Amy', 20006, 'verified', FALSE, 'usertoken_amy_secret'),
(7, '200000000000000007', 'Token User Tom', 20007, 'verified', FALSE, 'usertoken_tom_secret'),
(8, '200000000000000008', 'Key User Kim', 20008, 'verified', FALSE, 'usertoken_kim_secret'),
(9, '200000000000000009', 'Secret User Sam', 20009, 'verified', FALSE, 'usertoken_sam_secret');

-- Generate 66 more regular users
-- This is a simple loop structure for demonstration; in a real script, you might generate this programmatically.
-- For this file, we'll insert them manually.
INSERT INTO `user` (`discord_id`, `in_game_name`, `lodestone_id`, `status`, `admin`) VALUES
('300000000000000010', 'Generic User 10', 30010, 'verified', FALSE),
('300000000000000011', 'Generic User 11', 30011, 'verified', FALSE),
('300000000000000012', 'Generic User 12', 30012, 'verified', FALSE),
('300000000000000013', 'Generic User 13', 30013, 'pending', FALSE),
('300000000000000014', 'Generic User 14', 30014, 'verified', FALSE),
('300000000000000015', 'Generic User 15', 30015, 'verified', FALSE),
('300000000000000016', 'Generic User 16', 30016, 'banned', FALSE),
('300000000000000017', 'Generic User 17', 30017, 'verified', FALSE),
('300000000000000018', 'Generic User 18', 30018, 'verified', FALSE),
('300000000000000019', 'Generic User 19', 30019, 'verified', FALSE),
('300000000000000020', 'Generic User 20', 30020, 'verified', FALSE),
('300000000000000021', 'Generic User 21', 30021, 'verified', FALSE),
('300000000000000022', 'Generic User 22', 30022, 'verified', FALSE),
('300000000000000023', 'Generic User 23', 30023, 'verified', FALSE),
('300000000000000024', 'Generic User 24', 30024, 'verified', FALSE),
('300000000000000025', 'Generic User 25', 30025, 'verified', FALSE),
('300000000000000026', 'Generic User 26', 30026, 'verified', FALSE),
('300000000000000027', 'Generic User 27', 30027, 'verified', FALSE),
('300000000000000028', 'Generic User 28', 30028, 'verified', FALSE),
('300000000000000029', 'Generic User 29', 30029, 'verified', FALSE),
('300000000000000030', 'Generic User 30', 30030, 'verified', FALSE),
('300000000000000031', 'Generic User 31', 30031, 'verified', FALSE),
('300000000000000032', 'Generic User 32', 30032, 'verified', FALSE),
('300000000000000033', 'Generic User 33', 30033, 'verified', FALSE),
('300000000000000034', 'Generic User 34', 30034, 'verified', FALSE),
('300000000000000035', 'Generic User 35', 30035, 'verified', FALSE),
('300000000000000036', 'Generic User 36', 30036, 'verified', FALSE),
('300000000000000037', 'Generic User 37', 30037, 'verified', FALSE),
('300000000000000038', 'Generic User 38', 30038, 'verified', FALSE),
('300000000000000039', 'Generic User 39', 30039, 'verified', FALSE),
('300000000000000040', 'Generic User 40', 30040, 'verified', FALSE),
('300000000000000041', 'Generic User 41', 30041, 'verified', FALSE),
('300000000000000042', 'Generic User 42', 30042, 'verified', FALSE),
('300000000000000043', 'Generic User 43', 30043, 'verified', FALSE),
('300000000000000044', 'Generic User 44', 30044, 'verified', FALSE),
('300000000000000045', 'Generic User 45', 30045, 'verified', FALSE),
('300000000000000046', 'Generic User 46', 30046, 'verified', FALSE),
('300000000000000047', 'Generic User 47', 30047, 'verified', FALSE),
('300000000000000048', 'Generic User 48', 30048, 'verified', FALSE),
('300000000000000049', 'Generic User 49', 30049, 'verified', FALSE),
('300000000000000050', 'Generic User 50', 30050, 'verified', FALSE),
('300000000000000051', 'Generic User 51', 30051, 'verified', FALSE),
('300000000000000052', 'Generic User 52', 30052, 'verified', FALSE),
('300000000000000053', 'Generic User 53', 30053, 'verified', FALSE),
('300000000000000054', 'Generic User 54', 30054, 'verified', FALSE),
('300000000000000055', 'Generic User 55', 30055, 'verified', FALSE),
('300000000000000056', 'Generic User 56', 30056, 'verified', FALSE),
('300000000000000057', 'Generic User 57', 30057, 'verified', FALSE),
('300000000000000058', 'Generic User 58', 30058, 'verified', FALSE),
('300000000000000059', 'Generic User 59', 30059, 'verified', FALSE),
('300000000000000060', 'Generic User 60', 30060, 'verified', FALSE),
('300000000000000061', 'Generic User 61', 30061, 'verified', FALSE),
('300000000000000062', 'Generic User 62', 30062, 'verified', FALSE),
('300000000000000063', 'Generic User 63', 30063, 'verified', FALSE),
('300000000000000064', 'Generic User 64', 30064, 'verified', FALSE),
('300000000000000065', 'Generic User 65', 30065, 'verified', FALSE),
('300000000000000066', 'Generic User 66', 30066, 'verified', FALSE),
('300000000000000067', 'Generic User 67', 30067, 'verified', FALSE),
('300000000000000068', 'Generic User 68', 30068, 'verified', FALSE),
('300000000000000069', 'Generic User 69', 30069, 'verified', FALSE),
('300000000000000070', 'Generic User 70', 30070, 'verified', FALSE),
('300000000000000071', 'Generic User 71', 30071, 'verified', FALSE),
('300000000000000072', 'Generic User 72', 30072, 'verified', FALSE),
('300000000000000073', 'Generic User 73', 30073, 'verified', FALSE),
('300000000000000074', 'Generic User 74', 30074, 'verified', FALSE),
('300000000000000075', 'Generic User 75', 30075, 'verified', FALSE);


-- Insert Seasons
INSERT INTO `season` (`id`, `number`, `name`, `start_date`, `end_date`) VALUES
(1, 1, 'Season of Awakening', '2025-01-01 00:00:00', '2025-03-31 23:59:59'),
(2, 2, 'Season of the Elements', '2025-06-01 00:00:00', '2025-08-31 23:59:59'),
(3, 3, 'Season of the Stars', '2025-10-01 00:00:00', '2025-12-31 23:59:59');

-- Insert Ranks
INSERT INTO `rank` (`id`, `name`, `badge_url`) VALUES
(1, 'Bronze', 'https://example.com/badges/bronze.png'),
(2, 'Silver', 'https://example.com/badges/silver.png'),
(3, 'Gold', 'https://example.com/badges/gold.png'),
(4, 'Platinum', 'https://example.com/badges/platinum.png'),
(5, 'Diamond', 'https://example.com/badges/diamond.png');

-- Insert Prizes
INSERT INTO `prize` (`description`, `value`, `lodestone_id`, `discord_role`) VALUES
('100,000 Gil', 100000, NULL, NULL),
('500,000 Gil', 500000, NULL, NULL),
('1,000,000 Gil', 1000000, NULL, NULL),
('Exclusive "Bronze Contender" Discord Role', NULL, NULL, 900000000000000001),
('Exclusive "Silver Contender" Discord Role', NULL, NULL, 900000000000000002),
('Exclusive "Gold Contender" Discord Role', NULL, NULL, 900000000000000003),
('Exclusive "Elemental Champion" Discord Role', NULL, NULL, 900000000000000004),
('Aetheryte Ticket x99', 99, 12345, NULL),
('Wind-up Sun Minion', 1, 54321, NULL),
('Gilded Magitek Mount', 1, 67890, NULL);

-- Insert Items (approx 100)
INSERT INTO `item` (`name`, `lodestone_id`) VALUES
('Oak Log', 5001), ('Yew Log', 5002), ('Maple Log', 5003), ('Teak Log', 5004), ('Mahogany Log', 5005),
('Pine Log', 5006), ('Spruce Log', 5007), ('Cedar Log', 5008), ('Willow Log', 5009), ('Rosewood Log', 5010),
('Copper Ore', 6001), ('Tin Ore', 6002), ('Iron Ore', 6003), ('Silver Ore', 6004), ('Gold Ore', 6005),
('Mythril Ore', 6006), ('Cobalt Ore', 6007), ('Darksteel Ore', 6008), ('Titanium Ore', 6009), ('Adamantite Ore', 6010),
('Raw Amethyst', 7001), ('Raw Ruby', 7002), ('Raw Sapphire', 7003), ('Raw Emerald', 7004), ('Raw Diamond', 7005),
('Fire Shard', 8001), ('Ice Shard', 8002), ('Wind Shard', 8003), ('Earth Shard', 8004), ('Lightning Shard', 8005), ('Water Shard', 8006),
('Fire Crystal', 8011), ('Ice Crystal', 8012), ('Wind Crystal', 8013), ('Earth Crystal', 8014), ('Lightning Crystal', 8015), ('Water Crystal', 8016),
('Fire Cluster', 8021), ('Ice Cluster', 8022), ('Wind Cluster', 8023), ('Earth Cluster', 8024), ('Lightning Cluster', 8025), ('Water Cluster', 8026),
('Cotton Boll', 9001), ('Flax', 9002), ('Hemp', 9003), ('Silkworm Cocoon', 9004), ('Ramie', 9005),
('Diremite Web', 11001), ('Bat Wing', 11002), ('Beastkin Blood', 11003), ('Hippo-leather', 11004), ('Raptor Sinew', 11005),
('Aldgoat Horn', 11006), ('Gelato Flesh', 11007), ('Pudding Flesh', 11008), ('Wolf Fang', 11009), ('Bear Fat', 11010),
('Table Salt', 12001), ('Mineral Water', 12002), ('Wild Onion', 12003), ('Garlean Garlic', 12004), ('Black Pepper', 12005),
('Popoto', 12006), ('Cieldalaes Pineapple', 12007), ('La Noscean Orange', 12008), ('Lowland Grapes', 12009), ('Sun Lemon', 12010),
('Maple Sap', 13001), ('Rubber', 13002), ('Varnish', 13003), ('Beeswax', 13004), ('Fish Glue', 13005),
('Silver Sand', 14001), ('Limestone', 14002), ('Obsidian', 14003), ('Granite', 14004), ('Marble', 14005),
('Megalocrab Shell', 15001), ('Coral Butterfly', 15002), ('Tiger Cod', 15003), ('Silver Shark', 15004), ('Mazlaya Marlin', 15005),
('Pipira Pira', 15006), ('Harbor Herring', 15007), ('Sea Pickle', 15008), ('Nepto Dragon', 15009), ('Coelacanth', 15010),
('Crawler Cocoon', 16001), ('Antling Mandible', 16002), ('Manticore Hair', 16003), ('Wyvern Wing', 16004), ('Dragon Blood', 16005);


-- --- Relational Data Insertion ---

-- Enroll users in seasons
-- Let's enroll almost everyone in the past and current season
INSERT INTO `season_user` (`user_id`, `season_id`)
SELECT `id`, 1 FROM `user` WHERE `id` <= 70;
INSERT INTO `season_user` (`user_id`, `season_id`)
SELECT `id`, 2 FROM `user` WHERE `id` <= 75;

-- Define items and points for Season 1
INSERT INTO `season_item` (`season_id`, `item_id`, `point_value`) VALUES
(1, 1, 5), (1, 11, 10), (1, 21, 20), (1, 31, 1), (1, 41, 2), (1, 51, 15), (1, 61, 25), (1, 71, 30), (1, 81, 40), (1, 91, 5);

-- Define items and points for Season 2 (current)
INSERT INTO `season_item` (`season_id`, `item_id`, `point_value`) VALUES
(2, 31, 5), (2, 32, 5), (2, 33, 5), (2, 34, 5), (2, 35, 5), (2, 36, 5), -- Shards are 5 points
(2, 41, 15), (2, 42, 15), (2, 43, 15), (2, 44, 15), (2, 45, 15), (2, 46, 15), -- Crystals are 15 points
(2, 51, 50), (2, 52, 50), (2, 53, 50), (2, 54, 50), (2, 55, 50), (2, 56, 50), -- Clusters are 50 points
(2, 1, 10), (2, 2, 12), (2, 11, 20), (2, 12, 25), (2, 61, 100), (2, 99, 250); -- Misc items

-- Define ranks for Season 1
INSERT INTO `season_rank` (`season_id`, `rank_id`, `number`, `required_points`) VALUES
(1, 1, 1, 100), (1, 2, 2, 500), (1, 3, 3, 1500), (1, 4, 4, 5000), (1, 5, 5, 10000);

-- Define ranks for Season 2 (different order and points)
INSERT INTO `season_rank` (`season_id`, `rank_id`, `number`, `required_points`) VALUES
(2, 1, 5, 250), (2, 2, 4, 1000), (2, 3, 3, 3000), (2, 4, 2, 8000), (2, 5, 1, 20000);

-- Define prizes for Season 1 ranks
INSERT INTO `season_prize` (`season_rank_id`, `prize_id`) VALUES
(1, 1), (1, 4), (2, 2), (2, 5), (3, 3), (3, 6), (4, 8), (5, 9);

-- Define prizes for Season 2 ranks
INSERT INTO `season_prize` (`season_rank_id`, `prize_id`) VALUES
(6, 1), (6, 4), (7, 2), (7, 5), (8, 3), (8, 6), (9, 7), (10, 10);

-- --- Transactional Data ---
-- Insert Submissions (this will be a sample, a real app would generate many more)
-- Let's make user 5 a high-scorer in season 2
INSERT INTO `submission` (`user_id`, `season_item_id`, `quantity`, `total_point_value`) VALUES
(5, 11, 10, 50), -- 10 fire shards
(5, 17, 5, 75),  -- 5 fire crystals
(5, 23, 2, 100), -- 2 fire clusters
(10, 11, 2, 10), -- user 10 submits 2 fire shards
(11, 12, 5, 25), -- user 11 submits 5 ice shards
(12, 18, 1, 15), -- user 12 submits 1 ice crystal
(5, 28, 1, 100), -- user 5 submits a rare item
(15, 11, 20, 100),
(20, 17, 10, 150),
(25, 24, 4, 200),
(5, 29, 1, 250),
(30, 11, 5, 25);


-- --- Data Aggregation ---
-- In a real application, this would be handled by triggers or application logic.
-- For this test data setup, we'll run a manual update to populate the denormalized total_points.

-- Update total_points for season 2
UPDATE `season_user` su
SET su.total_points = (
    SELECT SUM(s.total_point_value)
    FROM `submission` s
    JOIN `season_item` si ON s.season_item_id = si.id
    WHERE s.user_id = su.user_id AND si.season_id = su.season_id
)
WHERE su.season_id = 2;

-- Award ranks based on the new totals for season 2
INSERT INTO `season_user_rank` (`user_id`, `season_rank_id`)
SELECT su.user_id, sr.id
FROM `season_user` su
JOIN `season_rank` sr ON su.season_id = sr.season_id
WHERE su.total_points >= sr.required_points
AND su.season_id = 2;


