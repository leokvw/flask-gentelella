DROP DATABASE IF EXISTS access_control;
CREATE DATABASE access_control DEFAULT CHARACTER SET UTF8MB4;
USE access_control;

CREATE TABLE `user`
(
    `id`       VARCHAR(20) NOT NULL COMMENT '物业管理人员身份证号,最多不超过20个字符',
    `name`     VARCHAR(20) NOT NULL COMMENT '物业管理人员名字,最多不超过20个字符',
    `mobile`   VARCHAR(20) NOT NULL COMMENT '物业管理人员手机号码最多不超过20个字符',
    `password` VARCHAR(32)  DEFAULT '123456' COMMENT '物业管理人员登录密码,最多不超过32个字符',
    CONSTRAINT PK_administrator PRIMARY KEY (`id`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '物业管理人员信息,插入数据时至少需提供所属部门,身份证号,名字以及手机号';

CREATE TABLE `building`
(
    `number`      TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    CONSTRAINT PK_building PRIMARY KEY (`number`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '住宅楼信息,插入数据时需提供住宅楼,楼层数以及每层房间数';

-- DROP TABLE IF EXISTS `resident`;
CREATE TABLE `resident`
(
    `id`           VARCHAR(20)     NOT NULL COMMENT '住户身份证号,最多不超过20个字符',
    `name`         VARCHAR(20)     NOT NULL COMMENT '住户名字,最多不超过20个字符',
    `mobile`       VARCHAR(20) COMMENT '住户手机号码,最多不超过20个字符,考虑小孩子或者其他情况可能无手机号',
    `portrait`     VARCHAR(100)        DEFAULT 'undefined_portrait.png' COMMENT '住户头像路径,最多不超过100个字符',
    `password`     VARCHAR(32)         DEFAULT '123456' COMMENT '住户登录密码,默认密码为123456,最多不超过32个字符',
    `number`       TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    CONSTRAINT PK_resident PRIMARY KEY (`id`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '住户信息,插入数据时至少需提供房间唯一编号,住户身份证号及姓名';

CREATE TABLE `visitor`
(
    `id`        SERIAL COMMENT '访客登记号,值范围为1-18446744073709551615',
    `name`      VARCHAR(20)     NOT NULL COMMENT '访客姓名,最多不超过20个字符',
    `building_id`   BIGINT UNSIGNED NOT NULL COMMENT '目标房间唯一编号,值范围为1-18446744073709551615',
    `is_expire` BOOLEAN         NOT NULL COMMENT '访客限定期限是否到期:0-仍在期限内,1-超过期限',
    CONSTRAINT PK_visitor PRIMARY KEY (`id`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '访客信息';

CREATE TABLE `capture_record`
(
    `id`           SERIAL COMMENT '记录的序号,值范围为1-18446744073709551615',
    `on_record`    BOOLEAN DEFAULT FALSE COMMENT '采集到的人脸图像是否符合数据库中原有的人脸数据,0-不符合,1-符合',
    `building`     TINYINT UNSIGNED NOT NULL COMMENT '采集摄像头所属住宅楼号,值范围为0-255',
    CONSTRAINT PK_capture_record PRIMARY KEY (`id`),
    CONSTRAINT FK_capture_record_building FOREIGN KEY (`building`) REFERENCES `building` (`number`) ON UPDATE CASCADE ON DELETE CASCADE
) DEFAULT CHARSET = UTF8MB4 COMMENT '摄像头采集记录';

CREATE TABLE `access_record`
(
    `id`        BIGINT UNSIGNED NOT NULL COMMENT '成功进出记录号,值范围为1-18446744073709551615',
    `direction` BOOLEAN    DEFAULT 0 COMMENT '进出方向,0-进入,1-出门,默认进门',
    `type`      TINYINT(2) DEFAULT 0 COMMENT '0-住户,1-物业管理人员,2-访客,3-未知,默认住户进出',
    `method`    TINYINT(2) DEFAULT 0 COMMENT '0-面部识别进入,1-客户端手动开门,2-使用钥匙,3-手动开门',
    CONSTRAINT PK_access_record PRIMARY KEY (`id`),
    CONSTRAINT FK_access_record_capture_record FOREIGN KEY (`id`) REFERENCES `capture_record` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
) DEFAULT CHARSET = UTF8MB4 COMMENT '进出记录';
