ALTER TABLE `apk_merge`.`update`
MODIFY COLUMN `download_link_id` int UNSIGNED NULL COMMENT '下载链接id' AFTER `size`;

ALTER TABLE `apk_merge`.`app`
MODIFY COLUMN `app_link_id` int UNSIGNED NULL COMMENT 'app详解链接地址id' AFTER `apk_name`;

DROP PROCEDURE IF EXISTS `apk_merge`.`insert_app_update`;
delimiter ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_app_update`(IN `title_in` char(255),IN `name_in` char(255),IN `app_link_in` varchar(1023),IN `developer_in` VARCHAR(255),IN `type_in` varchar(255),IN `market_in` varchar(255),IN `version_in` char(255),IN `size_in` char(20),IN `download_link_in` varchar(1023),IN `update_date_in` DATETIME)
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

DROP PROCEDURE IF EXISTS `apk_merge`.`insert_app_from_file`;
delimiter ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_app_from_file`(IN `title_in` char(255),IN `name_in` char(255),IN `developer_in` VARCHAR(255),IN `type_in` varchar(255),IN `market_in` varchar(255),IN `version_in` char(255),IN `size_in` char(20),IN `update_date_in` DATETIME,IN `apk_hash_in` CHAR(64))
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