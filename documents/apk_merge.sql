/*
 Navicat Premium Data Transfer

 Source Server         : local_mysql_database
 Source Server Type    : MySQL
 Source Server Version : 80019
 Source Host           : localhost:3306
 Source Schema         : apk_merge

 Target Server Type    : MySQL
 Target Server Version : 80019
 File Encoding         : 65001

 Date: 15/12/2020 19:43:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app
-- ----------------------------
DROP TABLE IF EXISTS `app`;
CREATE TABLE `app`  (
  `app_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '应用id',
  `app_title` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '应用名称',
  `apk_name` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'apk包名',
  `app_link_id` int UNSIGNED NULL DEFAULT NULL COMMENT 'app详解链接地址id',
  `developer_id` mediumint UNSIGNED NOT NULL COMMENT '开发者id',
  `type_id` smallint UNSIGNED NOT NULL COMMENT 'app类型id',
  `market_id` tinyint UNSIGNED NOT NULL COMMENT '应用商城id',
  PRIMARY KEY (`app_id`) USING BTREE,
  UNIQUE INDEX `app_unique_index`(`apk_name`, `market_id`) USING BTREE COMMENT '唯一app由其平台和包名确定',
  INDEX `app.app_link_id`(`app_link_id`) USING BTREE,
  INDEX `app.type_id`(`type_id`) USING BTREE,
  INDEX `app.market_id`(`market_id`) USING BTREE,
  CONSTRAINT `app.app_link_id` FOREIGN KEY (`app_link_id`) REFERENCES `link` (`link_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `app.market_id` FOREIGN KEY (`market_id`) REFERENCES `market` (`market_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `app.type_id` FOREIGN KEY (`type_id`) REFERENCES `app_type` (`type_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'app表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for app_type
-- ----------------------------
DROP TABLE IF EXISTS `app_type`;
CREATE TABLE `app_type`  (
  `type_id` smallint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '类型',
  `type_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '类型名称',
  PRIMARY KEY (`type_id`) USING BTREE,
  UNIQUE INDEX `name`(`type_name`) USING BTREE COMMENT '类型名称唯一'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '应用类型表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for authority
-- ----------------------------
DROP TABLE IF EXISTS `authority`;
CREATE TABLE `authority`  (
  `authority_id` smallint UNSIGNED NOT NULL AUTO_INCREMENT,
  `authority_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '权限名称',
  PRIMARY KEY (`authority_id`) USING BTREE,
  UNIQUE INDEX `authority_name`(`authority_name`) USING BTREE COMMENT '权限名称唯一'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '权限名称表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for authority_relation
-- ----------------------------
DROP TABLE IF EXISTS `authority_relation`;
CREATE TABLE `authority_relation`  (
  `authority_relation_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '权限关系id',
  `update_id` int UNSIGNED NOT NULL COMMENT 'update id',
  `authority_id` smallint UNSIGNED NOT NULL COMMENT 'authority id',
  PRIMARY KEY (`authority_relation_id`) USING BTREE,
  UNIQUE INDEX `unique_authority_relation`(`update_id`, `authority_id`) USING BTREE COMMENT 'update_id和authority_id唯一确定',
  INDEX `authority_relation_authority_id`(`authority_id`) USING BTREE,
  CONSTRAINT `authority_relation_authority_id` FOREIGN KEY (`authority_id`) REFERENCES `authority` (`authority_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `authority_relation_update_id` FOREIGN KEY (`update_id`) REFERENCES `update` (`update_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'update 对应 authority的关系' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for developer
-- ----------------------------
DROP TABLE IF EXISTS `developer`;
CREATE TABLE `developer`  (
  `developer_id` mediumint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '开发者id',
  `developer_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '开发者名称',
  PRIMARY KEY (`developer_id`) USING BTREE,
  UNIQUE INDEX `name`(`developer_name`) USING BTREE COMMENT '开发者名称唯一'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '开发者表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for image
-- ----------------------------
DROP TABLE IF EXISTS `image`;
CREATE TABLE `image`  (
  `image_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '图片id',
  `image_link_id` int UNSIGNED NOT NULL COMMENT '图片链接id',
  `update_id` int UNSIGNED NOT NULL COMMENT '更新id',
  `is_download` bit(1) NOT NULL DEFAULT b'0' COMMENT '是否下载',
  PRIMARY KEY (`image_id`) USING BTREE,
  UNIQUE INDEX `image_unique_index`(`image_link_id`, `update_id`) USING BTREE COMMENT '更新id和图片链接地址唯一确定一张图片',
  INDEX `image.update_id`(`update_id`) USING BTREE,
  CONSTRAINT `image.image_link_id` FOREIGN KEY (`image_link_id`) REFERENCES `link` (`link_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `image.update_id` FOREIGN KEY (`update_id`) REFERENCES `update` (`update_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '图片表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for link
-- ----------------------------
DROP TABLE IF EXISTS `link`;
CREATE TABLE `link`  (
  `link_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '链接id',
  `href` varchar(1023) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '网址',
  PRIMARY KEY (`link_id`) USING BTREE,
  UNIQUE INDEX `href`(`href`) USING BTREE COMMENT '网址唯一'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '网页链接地址，采用不定长，独立分表优化update表的检索' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for market
-- ----------------------------
DROP TABLE IF EXISTS `market`;
CREATE TABLE `market`  (
  `market_id` tinyint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '应用商城id',
  `market_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '应用商城名字',
  PRIMARY KEY (`market_id`) USING BTREE,
  UNIQUE INDEX `market_name_unique_index`(`market_name`) USING BTREE COMMENT '应用商城名字唯一确定一个应用商城'
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '应用商城表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for update
-- ----------------------------
DROP TABLE IF EXISTS `update`;
CREATE TABLE `update`  (
  `update_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '更新id',
  `app_id` int UNSIGNED NOT NULL COMMENT '应用id',
  `version` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '版本号',
  `size` char(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '包大小',
  `download_link_id` int UNSIGNED NULL DEFAULT NULL COMMENT '下载链接id',
  `is_download` bit(1) NOT NULL DEFAULT b'0' COMMENT '是否下载',
  `apk_hash` binary(32) NULL DEFAULT NULL COMMENT 'apk sha256值',
  `malware` bit(1) NULL DEFAULT b'0' COMMENT '应用是否为恶意软件',
  `obfuscation` bit(1) NULL DEFAULT b'0' COMMENT '应用是否为加固混淆应用',
  `sdk_level` char(8) CHARACTER SET ascii COLLATE ascii_general_ci NULL DEFAULT NULL COMMENT 'sdk level',
  `update_date` datetime(0) NULL DEFAULT NULL COMMENT '更新日期',
  `is_delete` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标记',
  PRIMARY KEY (`update_id`) USING BTREE,
  UNIQUE INDEX `update_unique_index`(`app_id`, `version`) USING BTREE COMMENT 'app id和版本号唯一确定一个更新',
  INDEX `update.download_link_id`(`download_link_id`) USING BTREE,
  CONSTRAINT `update.app_id` FOREIGN KEY (`app_id`) REFERENCES `app` (`app_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `update.download_link_id` FOREIGN KEY (`download_link_id`) REFERENCES `link` (`link_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '应用版本更新表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Procedure structure for insert_app_from_file
-- ----------------------------
DROP PROCEDURE IF EXISTS `insert_app_from_file`;
delimiter ;;
CREATE PROCEDURE `insert_app_from_file`(IN `title_in` char(255),IN `name_in` char(255),IN `developer_in` VARCHAR(255),IN `type_in` varchar(255),IN `market_in` varchar(255),IN `version_in` char(255),IN `size_in` char(20),IN `update_date_in` DATETIME,IN `apk_hash_in` CHAR(64))
BEGIN
	# declare local variables
	DECLARE local_market_id TINYINT UNSIGNED;
	DECLARE local_type_id SMALLINT UNSIGNED;
	DECLARE local_developer_id MEDIUMINT UNSIGNED;
	DECLARE local_app_id INT UNSIGNED;
	
	# save the market
	INSERT IGNORE INTO market(market_name) VALUES(market_in);
	SELECT market_id INTO local_market_id FROM market WHERE market_name=market_in;
	
	# save the type
	INSERT IGNORE INTO app_type(type_name) VALUES(type_in);
	SELECT type_id INTO local_type_id FROM app_type WHERE type_name=type_in;
	
	# save the developer
	INSERT IGNORE INTO developer(developer_name) VALUES(developer_in);
	SELECT developer_id INTO local_developer_id FROM developer WHERE developer_name=developer_in;
	
	# save the app
	INSERT IGNORE INTO app(app_title, apk_name, developer_id, type_id, market_id) VALUES(title_in, name_in, local_developer_id, local_type_id, local_market_id);
	SELECT app_id INTO local_app_id FROM app WHERE apk_name=name_in AND market_id=local_market_id;
	
	# save the update
	INSERT IGNORE INTO `update`(app_id, version, size, is_download, apk_hash, update_date) VALUES(local_app_id, version_in, size_in, TRUE, UNHEX(apk_hash_in), update_date_in);
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for insert_app_update
-- ----------------------------
DROP PROCEDURE IF EXISTS `insert_app_update`;
delimiter ;;
CREATE PROCEDURE `insert_app_update`(IN `title_in` char(255),IN `name_in` char(255),IN `app_link_in` varchar(1023),IN `developer_in` VARCHAR(255),IN `type_in` varchar(255),IN `market_in` varchar(255),IN `version_in` char(255),IN `size_in` char(20),IN `download_link_in` varchar(1023),IN `update_date_in` DATETIME)
BEGIN
	# declare local variables
	DECLARE local_app_link_id INT UNSIGNED;
	DECLARE local_download_link_id INT UNSIGNED;
	DECLARE local_market_id TINYINT UNSIGNED;
	DECLARE local_type_id SMALLINT UNSIGNED;
	DECLARE local_developer_id MEDIUMINT UNSIGNED;
	DECLARE local_app_id INT UNSIGNED;

	# save the link
	INSERT IGNORE INTO link(href) VALUES(app_link_in), (download_link_in);
	SELECT link_id INTO local_app_link_id FROM link WHERE href=app_link_in;
	SELECT link_id INTO local_download_link_id FROM link WHERE href=download_link_in;
	
	# save the market
	INSERT IGNORE INTO market(market_name) VALUES(market_in);
	SELECT market_id INTO local_market_id FROM market WHERE market_name=market_in;
	
	# save the type
	INSERT IGNORE INTO app_type(type_name) VALUES(type_in);
	SELECT type_id INTO local_type_id FROM app_type WHERE type_name=type_in;
	
	# save the developer
	INSERT IGNORE INTO developer(developer_name) VALUES(developer_in);
	SELECT developer_id INTO local_developer_id FROM developer WHERE developer_name=developer_in;
	
	# save the app
	INSERT IGNORE INTO app(app_title, apk_name, app_link_id, developer_id, type_id, market_id) VALUES(title_in, name_in, local_app_link_id, local_developer_id, local_type_id, local_market_id)
		ON  DUPLICATE KEY
		UPDATE app_title=title_in, app_link_id=local_app_link_id, developer_id=local_developer_id, type_id=local_type_id;
	SELECT app_id INTO local_app_id FROM app WHERE apk_name=name_in AND market_id=local_market_id;
	
	# save the update
	INSERT IGNORE INTO `update`(app_id, version, size, download_link_id, update_date) VALUES(local_app_id, version_in, size_in, local_download_link_id, update_date_in)
		ON DUPLICATE KEY
		UPDATE size=size_in, download_link_id=local_download_link_id, update_date=update_date_in;
	SELECT update_id FROM `update` WHERE app_id=local_app_id AND version=version_in;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for insert_authority_relation
-- ----------------------------
DROP PROCEDURE IF EXISTS `insert_authority_relation`;
delimiter ;;
CREATE PROCEDURE `insert_authority_relation`(IN `hash_in` CHAR(64),IN `authority_name_in` varchar(255))
BEGIN
	# declare local variables
	DECLARE local_update_id INT UNSIGNED;
	DECLARE local_authority_id SMALLINT UNSIGNED;
	DECLARE done INT DEFAULT 0;
	DECLARE report CURSOR FOR SELECT update_id FROM `update` WHERE apk_hash=UNHEX(hash_in);
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=1;
	
	# save the authority
	INSERT IGNORE INTO authority(authority_name) VALUES(authority_name_in);
	SELECT authority_id INTO local_authority_id FROM authority WHERE authority_name=authority_name_in;
	
	# get the update_id
	OPEN report;  # open the cursor
		FETCH report INTO local_update_id;
		WHILE done<>1 DO
			INSERT IGNORE INTO authority_relation(update_id, authority_id) VALUES(local_update_id, local_authority_id);
			FETCH report INTO local_update_id;
		END WHILE;
	CLOSE report;  # close the cursor
			
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for insert_image
-- ----------------------------
DROP PROCEDURE IF EXISTS `insert_image`;
delimiter ;;
CREATE PROCEDURE `insert_image`(IN `link_in` varchar(1023),IN `update_id_in` int unsigned)
BEGIN
	# declare the local variables
	DECLARE local_link_id INT UNSIGNED;
	
	# save the link
	INSERT IGNORE INTO link(href) VALUES(link_in);
	SELECT link_id INTO local_link_id FROM link WHERE href=link_in;
	
	# save the image
	INSERT IGNORE INTO image(image_link_id, update_id) VALUES(local_link_id, update_id_in);
	SELECT image_id FROM image WHERE image_link_id=local_link_id AND update_id=update_id_in;
	
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for set_image_available
-- ----------------------------
DROP PROCEDURE IF EXISTS `set_image_available`;
delimiter ;;
CREATE PROCEDURE `set_image_available`(IN `image_id_in` int unsigned)
BEGIN
	UPDATE image SET is_download=TRUE
		WHERE image_id=image_id_in;

END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for set_update_available
-- ----------------------------
DROP PROCEDURE IF EXISTS `set_update_available`;
delimiter ;;
CREATE PROCEDURE `set_update_available`(IN `update_id_in` int unsigned, IN `size_in` char(20), IN `hash_in` char(64))
BEGIN
	UPDATE `update` SET is_download=TRUE, size=size_in, apk_hash=UNHEX(hash_in)
		WHERE update_id=update_id_in;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
