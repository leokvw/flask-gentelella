DROP DATABASE IF EXISTS access_control;
CREATE DATABASE access_control DEFAULT CHARACTER SET UTF8MB4;
USE access_control;

CREATE TABLE `admin`
(
    `id`       SERIAL      NOT NULL COMMENT '物业管理人员工号,最多不超过20个字符',
    `name`     VARCHAR(20) NOT NULL COMMENT '物业管理人员名字,最多不超过20个字符',
    `password` VARBINARY(200) COMMENT '物业管理人员登录密码,最多不超过32个字符,Base64加密',
    `create`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '管理人员信息创建时间,自动更新自动初始化',
    CONSTRAINT PK_administrator PRIMARY KEY (`id`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '物业管理人员信息';

CREATE TABLE `building`
(
    `number` TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    `name`   VARCHAR(20)      NOT NULL COMMENT '住宅楼名字，通常包含中文"楼"或者"#"',
    CONSTRAINT PK_building PRIMARY KEY (`number`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '住宅楼信息';

-- DROP TABLE IF EXISTS `resident`;
CREATE TABLE `resident`
(
    `id`            SERIAL COMMENT '住户唯一编号,值范围为1-18446744073709551615',
    `name`          VARCHAR(20)      NOT NULL COMMENT '住户名字,最多不超过20个字符',
    `mobile`        VARCHAR(20) COMMENT '住户手机号码,最多不超过20个字符,考虑小孩子或者其他情况可能无手机号',
    `portrait`      VARCHAR(100) COMMENT '住户头像路径,最多不超过100个字符，默认与id同名',
    `password`      VARCHAR(32)      NOT NULL COMMENT '住户登录密码,最多不超过32个字符',
    `building`      TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    `face_encoding` BLOB COMMENT '住户人脸特征向量序列化',
    `create`        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '住户信息创建时间,自动更新自动初始化',
    CONSTRAINT PK_resident PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (building) REFERENCES `building` (`number`) ON UPDATE CASCADE ON DELETE CASCADE
) DEFAULT CHARSET = UTF8MB4 COMMENT '住户信息';

CREATE TABLE `visitor`
(
    `id`        SERIAL COMMENT '访客登记号,值范围为1-18446744073709551615',
    `name`      VARCHAR(20)      NOT NULL COMMENT '访客姓名,最多不超过20个字符',
    `is_expire` BOOLEAN   DEFAULT 0 COMMENT '访客限定期限是否到期:0-仍在期限内,1-超过期限',
    `building`  TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    `create`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '访客信息创建时间,自动更新自动初始化',
    CONSTRAINT PK_visitor PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (building) REFERENCES `building` (`number`) ON UPDATE CASCADE ON DELETE CASCADE
) DEFAULT CHARSET = UTF8MB4 COMMENT '访客信息';

CREATE TABLE `capture`
(
    `id`        SERIAL COMMENT '记录的序号,值范围为1-18446744073709551615',
    `on_record` BOOLEAN   DEFAULT FALSE COMMENT '采集到的人脸图像是否符合数据库中原有的人脸数据,0-不符合,1-符合',
    `building`  TINYINT UNSIGNED NOT NULL COMMENT '采集摄像头所属住宅楼号,值范围为0-255',
    `create`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '摄像头采集数据时间,自动更新自动初始化',
    CONSTRAINT PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (`building`) REFERENCES `building` (`number`) ON UPDATE CASCADE ON DELETE CASCADE
) DEFAULT CHARSET = UTF8MB4 COMMENT '摄像头采集记录';

CREATE TABLE `access`
(
    `id`        SERIAL COMMENT '成功进出记录号,值范围为1-18446744073709551615',
    `direction` BOOLEAN    DEFAULT 0 COMMENT '进出方向,0-进入,1-出门,默认进门',
    `type`      TINYINT(2) DEFAULT 0 COMMENT '0-住户,1-访客,2-未知,默认住户进出',
    `name`      VARCHAR(20) COMMENT '访客或者住户姓名,最多不超过20个字符',
    `building`  TINYINT UNSIGNED NOT NULL COMMENT '住宅楼楼号,值范围为0-255',
    `create`    TIMESTAMP  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '进出记录时间,自动更新自动初始化',
    CONSTRAINT PK_access_record PRIMARY KEY (`id`)
) DEFAULT CHARSET = UTF8MB4 COMMENT '进出记录';
