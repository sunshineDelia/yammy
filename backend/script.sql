-- =====================================================================
-- 南昌旅游美食推荐平台 — MySQL 数据库初始化脚本
-- ---------------------------------------------------------------------
-- 数据库名 : nanchang_travel
-- 表        : food(美食) / store(推荐门店) / attraction(景点) / favorite(收藏)
-- 引擎/字符集: InnoDB / utf8mb4
-- 兼容性    : MySQL 5.7+ / 8.0
-- 运行方式  : mysql -u root -p < backend/script.sql
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. 创建数据库
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `nanchang_travel`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `nanchang_travel`;

-- ---------------------------------------------------------------------
-- 2. 清理旧表（按外键依赖逆序删除，保证脚本可重复执行）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `favorite`;
DROP TABLE IF EXISTS `store`;
DROP TABLE IF EXISTS `attraction`;
DROP TABLE IF EXISTS `food`;

-- ---------------------------------------------------------------------
-- 3. 建表
-- ---------------------------------------------------------------------

-- 3.1 美食表
CREATE TABLE `food` (
  `id`          BIGINT         NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`        VARCHAR(100)   NOT NULL                COMMENT '美食名称',
  `description` TEXT           NOT NULL                COMMENT '简介',
  `avg_price`   DECIMAL(10, 2) NOT NULL                COMMENT '人均消费（元）',
  `image_url`   VARCHAR(255)            DEFAULT NULL   COMMENT '图片相对路径（静态资源）',
  `created_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = '南昌特色美食';

-- 3.2 推荐门店表（从属于美食）
CREATE TABLE `store` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `food_id`    BIGINT       NOT NULL                COMMENT '所属美食 ID（FK -> food.id）',
  `name`       VARCHAR(100) NOT NULL                COMMENT '门店名称',
  `address`    VARCHAR(255)          DEFAULT NULL   COMMENT '门店地址（可选）',
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_store_food_id` (`food_id`),
  CONSTRAINT `fk_store_food_id`
    FOREIGN KEY (`food_id`) REFERENCES `food` (`id`)
    ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = '美食推荐门店';

-- 3.3 景点表
CREATE TABLE `attraction` (
  `id`           BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`         VARCHAR(100) NOT NULL                COMMENT '景点名称',
  `description`  TEXT         NOT NULL                COMMENT '简介',
  `open_time`    VARCHAR(100) NOT NULL                COMMENT '开放时间',
  `ticket_price` VARCHAR(100) NOT NULL                COMMENT '门票参考（文本，支持「免费」「淡季/旺季」等）',
  `image_url`    VARCHAR(255)          DEFAULT NULL   COMMENT '图片相对路径（静态资源）',
  `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = '南昌旅游景点';

-- 3.4 收藏表（多态关联：target_type + target_id，不设外键，由 service 层校验目标存在）
CREATE TABLE `favorite` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '主键',
  `device_id`   VARCHAR(64) NOT NULL                COMMENT '匿名设备标识（前端生成 UUID，随 X-Device-Id 携带）',
  `target_type` VARCHAR(20) NOT NULL                COMMENT '收藏对象类型：food / attraction',
  `target_id`   BIGINT      NOT NULL                COMMENT '收藏对象 ID',
  `created_at`  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_favorite` (`device_id`, `target_type`, `target_id`),
  KEY `ix_favorite_device_id` (`device_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = '收藏（按匿名设备标识）';

-- =====================================================================
-- 完成。种子数据请通过 backend/seed/seed.py 写入（python -m seed.seed）。
-- =====================================================================
