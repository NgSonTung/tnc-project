const SubImageSchema = require("../model/SubImage");
const dbUtils = require("../utils/dbUtils");
const dbConfig = require("../database/dbconfig");
const DateTimeUtils = require("../utils/DateTimeUtils");

exports.addSubImageIfNotExisted = async (img) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  img.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = SubImageSchema.validateData(img);

  let query = `SET IDENTITY_INSERT ${SubImageSchema.schemaName} ON insert into ${SubImageSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(SubImageSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${SubImageSchema.schemaName} WHERE image = @image)` +
    ` SET IDENTITY_INSERT ${SubImageSchema.schemaName} OFF`;
  // console.log(query);

  let result = await request.query(query);

  // console.log(result);
  return result.recordsets;
};

exports.addImage = async (img) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  img.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = SubImageSchema.validateData(img);

  let query = `insert into ${SubImageSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(SubImageSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${SubImageSchema.schemaName} WHERE image = @image)`;

  let result = await request.query(query);

  // console.log(result);
  return result.recordsets;
};

exports.clearAll = async () => {
  query = `delete ${SubImageSchema.schemaName}  DBCC CHECKIDENT ('[${SubImageSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.getSubImgById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${SubImageSchema.schema.SubimgID.name}`,
      SubImageSchema.schema.SubimgID.sqlType,
      id
    )
    .query(
      `select * from ${SubImageSchema.schemaName} where ${SubImageSchema.schema.SubimgID.name} = @${SubImageSchema.schema.SubimgID.name}`
    );
  return result.recordsets[0][0];
};

exports.createNewSubImg = async (subImg) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!subImg) {
    throw new Error("Invalid input param");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  subImg.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  let insertData = SubImageSchema.validateData(subImg);
  let query = `insert into ${SubImageSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      SubImageSchema.schema,
      dbConfig.db.pool.request(),
      insertData
    );
  query += " (" + insertFieldNamesStr + ") values (" + insertValuesStr + ")";
  // console.log(query);
  let result = await request.query(query);
  return result.recordsets;
};

exports.deleteSubImgById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${SubImageSchema.schema.subimgID.name}`,
      SubImageSchema.schema.subimgID.sqlType,
      id
    )
    .query(
      `delete ${SubImageSchema.schemaName} where ${SubImageSchema.schema.subimgID.name} = @${SubImageSchema.schema.subimgID.name}`
    );
  return result.recordsets;
};

exports.updateSubImgById = async (id, updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!updateInfo) {
    throw new Error("Invalid input param");
  }

  let query = `update ${SubImageSchema.schemaName} set`;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    SubImageSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  if (!updateStr) {
    throw new Error("Invalid update param");
  }
  request.input(
    `${SubImageSchema.schema.subimgID.name}`,
    SubImageSchema.schema.subimgID.sqlType,
    id
  );
  query +=
    " " +
    updateStr +
    ` where ${SubImageSchema.schema.subimgID.name} = @${SubImageSchema.schema.subimgID.name}`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.getAllSubImages = async () => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request.query(
    `select * from ${SubImageSchema.schemaName}`
  );
  return result.recordsets[0];
};

exports.getProductSubImgById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${SubImageSchema.schema.ProductID.name}`,
      SubImageSchema.schema.ProductID.sqlType,
      id
    )
    .query(
      `select * from ${SubImageSchema.schemaName} where ${SubImageSchema.schema.ProductID.name} = @${SubImageSchema.schema.ProductID.name}`
    );
  return result.recordsets[0];
};
