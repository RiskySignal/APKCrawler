# `Document` Folder

存储数据库配置、数据库sql脚本及其他文档文件.

- `apk_merge.sql` 数据库sql脚本.
- `patch.2020-08-09.sql` 数据库sql脚本2020-08-09日补丁, 已在`apk_merge.sql`中修复该漏洞.
- `patch.2020-08-20.sql` 数据库sql脚本2020-08-20日补丁, 已在`apk_merge.sql`中修复该漏洞.
- `patch.2020-08-20-2.sql` 数据库sql脚本2020-08-20日补丁2，解决前一个补丁新增apk_hash字段导致的新增数据报错问题, 已在`apk_merge.sql`中修复该漏洞.
- `patch.2020-10-30.sql` 数据库sql脚本2020-10-30补丁，添加新的字段，已在`apk_merge.sql`中修复该漏洞
- `patch.2020-11-02.sql` 数据库sql脚本2020-11-02补丁，添加并更新存储过程，已在`apk_merge.sql`中修复该漏洞
- `patch.2020-12-15.sql` 数据库sql脚本2020-12-15补丁,  添加了从文件导入apk的存储过程, 并设置链接字段为 "可为空"的, 已在 `apk_merge.sql` 中修复该漏洞