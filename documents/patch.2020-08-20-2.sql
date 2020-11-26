DROP PROCEDURE IF EXISTS `apk_merge`.`set_update_available`;

delimiter ;;
CREATE
    DEFINER = `root`@`localhost` PROCEDURE `set_update_available`(IN `update_id_in` int unsigned, IN `size_in` char(20), IN `hash_in` char(64))
BEGIN
    UPDATE `update`
    SET is_download= TRUE,
        size=size_in,
        apk_hash=UNHEX(hash_in)
    WHERE update_id = update_id_in;
END;;
delimiter ;