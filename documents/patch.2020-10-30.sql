CREATE TABLE `apk_merge`.`authority`
(
    `authority_id`   smallint UNSIGNED                                       NOT NULL AUTO_INCREMENT,
    `authority_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    PRIMARY KEY (`authority_id`),
    UNIQUE INDEX `authority_name` (`authority_name`) USING BTREE COMMENT '权限名称唯一'
) COMMENT = '权限名称表';

CREATE TABLE `authority_relation`
(
    `authority_relation_id` int UNSIGNED      NOT NULL AUTO_INCREMENT COMMENT '权限关系id',
    `update_id`             int UNSIGNED      NOT NULL COMMENT 'update id',
    `authority_id`          smallint UNSIGNED NOT NULL COMMENT 'authority id',
    PRIMARY KEY (`authority_relation_id`) USING BTREE,
    INDEX `authority_relation_update_id` (`update_id`) USING BTREE,
    INDEX `authority_relation_authority_id` (`authority_id`) USING BTREE,
    CONSTRAINT `authority_relation_authority_id` FOREIGN KEY (`authority_id`) REFERENCES `authority` (`authority_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT `authority_relation_update_id` FOREIGN KEY (`update_id`) REFERENCES `update` (`update_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8
  COLLATE = utf8_general_ci COMMENT = 'update 对应 authority的关系'
  ROW_FORMAT = Dynamic;

ALTER TABLE `apk_merge`.`update`
    ADD COLUMN `malware`     bit(1)                                               NULL DEFAULT 0 COMMENT '应用是否为恶意软件' AFTER `apk_hash`,
    ADD COLUMN `obfuscation` bit(1)                                               NULL DEFAULT 0 COMMENT '应用是否为加固混淆应用' AFTER `malware`,
    ADD COLUMN `sdk_level`   char(8) CHARACTER SET ascii COLLATE ascii_general_ci NULL COMMENT 'sdk level' AFTER `obfuscation`;

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