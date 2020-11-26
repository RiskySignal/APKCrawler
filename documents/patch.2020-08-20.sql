ALTER TABLE `apk_merge`.`update`
    ADD COLUMN `apk_hash` binary(32) NULL COMMENT 'apk sha256值' AFTER `is_download`;