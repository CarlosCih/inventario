-- ============================================================
-- reset_db.sql
-- Elimina todas las tablas del proyecto (app + Django internos)
-- en orden correcto de dependencias (hijos antes que padres).
--
-- USO: Ejecutar en SQL Server Management Studio (SSMS) o sqlcmd
--      contra la base de datos del proyecto.
--
-- DESPUÉS de ejecutar este script:
--   1. python manage.py makemigrations
--   2. python manage.py migrate
--   3. python manage.py seed_catalogs   (opcional)
-- ============================================================

SET NOCOUNT ON;

PRINT '>> Eliminando tablas de la aplicación...';

-- ── transactions (depende de inventory, locations, auth) ──────────────────────
IF OBJECT_ID('transactions_inventorytransaction_tags', 'U') IS NOT NULL
    DROP TABLE transactions_inventorytransaction_tags;
PRINT '   transactions_inventorytransaction_tags';

IF OBJECT_ID('transactions_transactiondetail', 'U') IS NOT NULL
    DROP TABLE transactions_transactiondetail;
PRINT '   transactions_transactiondetail';

IF OBJECT_ID('transactions_inventorytransaction', 'U') IS NOT NULL
    DROP TABLE transactions_inventorytransaction;
PRINT '   transactions_inventorytransaction';

IF OBJECT_ID('transactions_transactiontag', 'U') IS NOT NULL
    DROP TABLE transactions_transactiontag;
PRINT '   transactions_transactiontag';

IF OBJECT_ID('transactions_transactionstatus', 'U') IS NOT NULL
    DROP TABLE transactions_transactionstatus;
PRINT '   transactions_transactionstatus';

IF OBJECT_ID('transactions_transactiontype', 'U') IS NOT NULL
    DROP TABLE transactions_transactiontype;
PRINT '   transactions_transactiontype';

-- ── inventory (depende de catalogs, locations) ────────────────────────────────
IF OBJECT_ID('inventory_asset', 'U') IS NOT NULL
    DROP TABLE inventory_asset;
PRINT '   inventory_asset';

IF OBJECT_ID('inventory_stock', 'U') IS NOT NULL
    DROP TABLE inventory_stock;
PRINT '   inventory_stock';

IF OBJECT_ID('inventory_item', 'U') IS NOT NULL
    DROP TABLE inventory_item;
PRINT '   inventory_item';

-- ── locations ─────────────────────────────────────────────────────────────────
IF OBJECT_ID('locations_location', 'U') IS NOT NULL
    DROP TABLE locations_location;
PRINT '   locations_location';

IF OBJECT_ID('locations_area', 'U') IS NOT NULL
    DROP TABLE locations_area;
PRINT '   locations_area';

IF OBJECT_ID('locations_locationtype', 'U') IS NOT NULL
    DROP TABLE locations_locationtype;
PRINT '   locations_locationtype';

-- ── catalogs ──────────────────────────────────────────────────────────────────
IF OBJECT_ID('catalogs_modelo', 'U') IS NOT NULL
    DROP TABLE catalogs_modelo;
PRINT '   catalogs_modelo';

IF OBJECT_ID('catalogs_marca', 'U') IS NOT NULL
    DROP TABLE catalogs_marca;
PRINT '   catalogs_marca';

IF OBJECT_ID('catalogs_categoria', 'U') IS NOT NULL
    DROP TABLE catalogs_categoria;
PRINT '   catalogs_categoria';

IF OBJECT_ID('catalogs_estado', 'U') IS NOT NULL
    DROP TABLE catalogs_estado;
PRINT '   catalogs_estado';

IF OBJECT_ID('catalogs_unitofmeasure', 'U') IS NOT NULL
    DROP TABLE catalogs_unitofmeasure;
PRINT '   catalogs_unitofmeasure';

-- ── Django internos ───────────────────────────────────────────────────────────
PRINT '>> Eliminando tablas internas de Django...';

IF OBJECT_ID('django_admin_log', 'U') IS NOT NULL
    DROP TABLE django_admin_log;
PRINT '   django_admin_log';

IF OBJECT_ID('django_session', 'U') IS NOT NULL
    DROP TABLE django_session;
PRINT '   django_session';

-- M2M auth
IF OBJECT_ID('auth_user_groups', 'U') IS NOT NULL
    DROP TABLE auth_user_groups;
PRINT '   auth_user_groups';

IF OBJECT_ID('auth_user_user_permissions', 'U') IS NOT NULL
    DROP TABLE auth_user_user_permissions;
PRINT '   auth_user_user_permissions';

IF OBJECT_ID('auth_group_permissions', 'U') IS NOT NULL
    DROP TABLE auth_group_permissions;
PRINT '   auth_group_permissions';

IF OBJECT_ID('auth_user', 'U') IS NOT NULL
    DROP TABLE auth_user;
PRINT '   auth_user';

IF OBJECT_ID('auth_group', 'U') IS NOT NULL
    DROP TABLE auth_group;
PRINT '   auth_group';

IF OBJECT_ID('auth_permission', 'U') IS NOT NULL
    DROP TABLE auth_permission;
PRINT '   auth_permission';

IF OBJECT_ID('django_content_type', 'U') IS NOT NULL
    DROP TABLE django_content_type;
PRINT '   django_content_type';

IF OBJECT_ID('django_migrations', 'U') IS NOT NULL
    DROP TABLE django_migrations;
PRINT '   django_migrations';

PRINT '';
PRINT '>> Listo. La base de datos está limpia.';
PRINT '>> Siguiente paso: python manage.py makemigrations && python manage.py migrate';
