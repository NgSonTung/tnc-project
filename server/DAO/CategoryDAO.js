const dbConfig = require("../database/dbconfig");
const CategorySchema = require("../Model/Category");
const DTOCategory = require("../DTO/Default/DTOCategory");
const dbUtils = require("../utils/dbUtils");
const DateTimeUtils = require("../utils/DateTimeUtils");

exports.addCateIfNotExists = async (cate) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  cate.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = CategorySchema.validateData(cate);
  let query = `SET IDENTITY_INSERT ${CategorySchema.schemaName} ON insert into ${CategorySchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(CategorySchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${CategorySchema.schemaName} WHERE categoryName = @categoryName)` +
    ` SET IDENTITY_INSERT ${CategorySchema.schemaName} OFF`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.clearAll = async () => {
  query = `delete ${CategorySchema.schemaName}  DBCC CHECKIDENT ('[${CategorySchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};
exports.getCategories = async () => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request.query(`select * from category`);
  var dtos = result.recordsets[0].map((x) => new DTOCategory(x));
  return dtos;
};

exports.getCategoryIdByName = async (name) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${CategorySchema.schema.CategoryName.name}`,
      CategorySchema.schema.CategoryName.sqlType,
      name
    )
    .query(
      `select CategoryID from ${CategorySchema.schemaName} where ${CategorySchema.schema.CategoryName.name} = @${CategorySchema.schema.CategoryName.name}`
    );
  return result.recordsets[0][0].CategoryID;
};

exports.getCategoryById = async (id) => {
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${CategorySchema.schema.CategoryName.name}`,
      CategorySchema.schema.CategoryName.sqlType,
      id
    )
    .query(
      `select * from ${CategorySchema.schemaName} where ${CategorySchema.schema.CategoryName.name} = @${CategorySchema.schema.CategoryName.name}`
    );
  if (result.recordsets[0][0]) {
    return new DTOCategory(result.recordsets[0][0]);
  }
  return result.recordsets[0][0];
};
