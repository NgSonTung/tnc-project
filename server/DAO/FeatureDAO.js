const FeatureSchema = require("../model/Feature");
const dbConfig = require("../database/dbconfig");
const dbUtils = require("../utils/dbUtils");
const DTOFeature = require("../DTO/Default/DTOFeature");
const DateTimeUtils = require("../utils/DateTimeUtils");
exports.addFeatureIfNotExisted = async (feature) => {
  const dbPool = dbConfig.db.pool;
  if (!dbPool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  feature.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = FeatureSchema.validateData(feature);
  let query = `SET IDENTITY_INSERT ${FeatureSchema.schemaName} ON insert into ${FeatureSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(FeatureSchema.schema, dbPool.request(), insertData);
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }
  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${FeatureSchema.schemaName} WHERE feature = @feature)` +
    ` SET IDENTITY_INSERT ${FeatureSchema.schemaName} OFF`;
  let result = await request.query(query);
  return result.recordsets;
};
exports.clearAll = async () => {
  query = `delete ${FeatureSchema.schemaName}  DBCC CHECKIDENT ('[${FeatureSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.getFeatureById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${FeatureSchema.schema.FeatureID.name}`,
      FeatureSchema.schema.FeatureID.sqlType,
      id
    )
    .query(
      `select * from ${FeatureSchema.schemaName} where ${FeatureSchema.schema.FeatureID.name} = @${FeatureSchema.schema.FeatureID.name}`
    );
  return result.recordsets[0][0];
};

exports.getAllFeatures = async () => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request.query(`select * from ${FeatureSchema.schemaName}`);
  return result.recordsets[0];
};
exports.getFeaturesByProductId = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${FeatureSchema.schema.ProductID.name}`,
      FeatureSchema.schema.ProductID.sqlType,
      id
    )
    .query(
      `select * from ${FeatureSchema.schemaName} where ${FeatureSchema.schema.ProductID.name} = @${FeatureSchema.schema.ProductID.name}`
    );
  let dtos = result.recordsets[0].map((x) => new DTOFeature(x));
  return dtos;
};

exports.createNewFeature = async (feature) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!feature) {
    throw new Error("Invalid input param");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  feature.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  let insertData = FeatureSchema.validateData(feature);
  let query = `insert into ${FeatureSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      FeatureSchema.schema,
      dbConfig.db.pool.request(),
      insertData
    );
  query += " (" + insertFieldNamesStr + ") values (" + insertValuesStr + ")";
  // console.log(query);
  let result = await request.query(query);
  return result.recordsets;
};

exports.deleteFeatureById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${FeatureSchema.schema.FeatureID.name}`,
      FeatureSchema.schema.FeatureID.sqlType,
      id
    )
    .query(
      `delete from ${FeatureSchema.schemaName} where ${FeatureSchema.schema.FeatureID.name} = @${FeatureSchema.schema.FeatureID.name}`
    );
  return result.recordsets;
};

exports.updateFeatureById = async (id, updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!updateInfo) {
    throw new Error("Invalid input param");
  }

  let query = `update ${FeatureSchema.schemaName} set`;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    FeatureSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  if (!updateStr) {
    throw new Error("Invalid update param");
  }
  request.input(
    `${FeatureSchema.schema.FeatureID.name}`,
    FeatureSchema.schema.FeatureID.sqlType,
    id
  );
  query +=
    " " +
    updateStr +
    ` where ${FeatureSchema.schema.FeatureID.name} = @${FeatureSchema.schema.FeatureID.name}`;
  let result = await request.query(query);
  return result.recordsets;
};
