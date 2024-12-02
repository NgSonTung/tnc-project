const AuthSchema = require("../model/Auth");
const RefreshTokenSchema = require("../model/RefreshToken");
const dbConfig = require("../database/dbconfig");
const dbUtils = require("../utils/dbUtils");
const DateTimeUtils = require("../Utils/DateTimeUtils");
exports.addAuth = async (auth) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  const ms = DateTimeUtils.convertDateTimeToMilliseconds(
    new Date().toISOString()
  );
  console.log(ms);
  auth.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  console.log(auth.CreatedAt);
  let insertData = AuthSchema.validateData(auth);
  let query = `SET IDENTITY_INSERT ${AuthSchema.schemaName} ON insert into ${AuthSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(AuthSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }
  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${AuthSchema.schemaName} WHERE AuthName = @AuthName)` +
    ` SET IDENTITY_INSERT ${AuthSchema.schemaName} OFF`;
  await request.query(query);
};

exports.getRefreshTokenByUserID = async (id) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  let result = await dbConfig.db.pool
    .request()
    .input(
      RefreshTokenSchema.schema.UserID.name,
      RefreshTokenSchema.schema.UserID.sqlType,
      id
    )
    .query(
      `SELECT * from ${RefreshTokenSchema.schemaName} where ${RefreshTokenSchema.schema.UserID.name} = @${RefreshTokenSchema.schema.UserID.name}`
    );
  // console.log(result);
  return result.recordsets[0][0];
};

exports.getRefreshTokenByRefreshToken = async (refreshToken) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  let result = await dbConfig.db.pool
    .request()
    .input(
      RefreshTokenSchema.schema.RefreshToken.name,
      RefreshTokenSchema.schema.RefreshToken.sqlType,
      refreshToken
    )
    .query(
      `SELECT * from ${RefreshTokenSchema.schemaName} where ${RefreshTokenSchema.schema.RefreshToken.name} = @${RefreshTokenSchema.schema.RefreshToken.name}`
    );
  return result.recordsets[0][0];
};

exports.createRecordRefreshTokenByUserId = async (id) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }

  let result = await dbConfig.db.pool
    .request()
    .input(
      RefreshTokenSchema.schema.UserID.name,
      RefreshTokenSchema.schema.UserID.sqlType,
      id
    );
  const objRToken = {
    UserID: id,
    CreatedAt: new Date().toISOString(),
  };

  let insertData = RefreshTokenSchema.validateData(objRToken);
  let query = `insert into ${RefreshTokenSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      RefreshTokenSchema.schema,
      dbPool.request(),
      insertData
    );
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }
  query += " (" + insertFieldNamesStr + ") select  " + insertValuesStr;
  await request.query(query);
  // console.log(result);
  return result;
};

exports.updateRefreshTokenByUserId = async (id, updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!updateInfo) {
    throw new Error("Invalid input param");
  }

  if (!(await this.getRefreshTokenByUserID(id))) {
    await this.createRecordRefreshTokenByUserId(id);
  }
  if (updateInfo.Expires) {
    console.log(updateInfo.Expires);
  }
  let query = `update ${RefreshTokenSchema.schemaName} set`;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    RefreshTokenSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  if (!updateStr) {
    throw new Error("Invalid update param");
  }
  request.input(
    `${RefreshTokenSchema.schema.UserID.name}`,
    RefreshTokenSchema.schema.UserID.sqlType,
    id
  );
  query +=
    " " +
    updateStr +
    ` where ${RefreshTokenSchema.schema.UserID.name} = @${RefreshTokenSchema.schema.UserID.name}`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.deleteRefreshTokenByUserId = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const request = dbConfig.db.pool.request();
  request.input(
    `${RefreshTokenSchema.schema.UserID.name}`,
    RefreshTokenSchema.schema.UserID.sqlType,
    id
  );
  let query = `delete ${RefreshTokenSchema.schemaName} where ${RefreshTokenSchema.schema.RefreshToken.name} = @${RefreshTokenSchema.schema.RefreshToken.name}`;
  const result = await request.query(query);
  return result.recordsets;
};
exports.deleteRefreshTokenByRefreshToken = async (refreshToken) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const request = dbConfig.db.pool.request();
  request.input(
    `${RefreshTokenSchema.schema.RefreshToken.name}`,
    RefreshTokenSchema.schema.RefreshToken.sqlType,
    refreshToken
  );
  let query = `delete ${RefreshTokenSchema.schemaName} where ${RefreshTokenSchema.schema.RefreshToken.name} = @${RefreshTokenSchema.schema.RefreshToken.name}`;
  const result = await request.query(query);
  return result.recordsets;
};

exports.clearAll = async () => {
  query = `delete ${AuthSchema.schemaName}  DBCC CHECKIDENT ('[${AuthSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};
exports.cleanRToken = async () => {
  query = `delete ${RefreshTokenSchema.schemaName}  DBCC CHECKIDENT ('[${RefreshTokenSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};
