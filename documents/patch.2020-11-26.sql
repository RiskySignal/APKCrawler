
ALTER TABLE `apk_merge`.`app_type` COMMENT = '应用类型表';

ALTER TABLE `apk_merge`.`developer` COMMENT = '开发者表';

ALTER TABLE `apk_merge`.`update` COMMENT = '应用版本更新表';

ALTER TABLE `apk_merge`.`update`
ADD COLUMN `is_delete` bit(1) NOT NULL DEFAULT 0 COMMENT '删除标记' AFTER `update_date`;