const ModelSchemaValidator = require("./ModelSchemaValidator");
const ModelSchema = require("./ModelSchema");
const sql = require("mssql");
const AuthSchema = new ModelSchema(
  {
    AuthID: new ModelSchemaValidator({
      name: "AuthID",
      sqlType: sql.Int,
    }),
    AuthName: new ModelSchemaValidator({
      name: "AuthName",
      sqlType: sql.NVarChar,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Auth",
  "CreatedAt"
);

module.exports = AuthSchema;
