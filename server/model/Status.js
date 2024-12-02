const ModelSchemaValidator = require("./ModelSchemaValidator");
const ModelSchema = require("./ModelSchema");
const sql = require("mssql");
const StatusSchema = new ModelSchema(
  {
    StatusID: new ModelSchemaValidator({
      name: "StatusID",
      sqlType: sql.Int,
    }),
    StatusName: new ModelSchemaValidator({
      name: "StatusName",
      sqlType: sql.NVarChar,
    }),
    TypeStatus: new ModelSchemaValidator({
      name: "TypeStatus",
      sqlType: sql.Int,
      default: 1,
    }),
    Mark: new ModelSchemaValidator({
      StatusName: "Mark",
      sqlType: sql.NVarChar,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "LS_Status",
  "CreatedAt"
);

module.exports = StatusSchema;
