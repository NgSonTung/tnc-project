const sql = require("mssql");
const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const StaticData = require("../utils/StaticData");

const RefreshTokenSchema = new ModelSchema(
  {
    ID: new ModelSchemaValidator({
      name: "ID",
      sqlType: sql.Int,
    }),
    UserID: new ModelSchemaValidator({
      name: "UserID",
      sqlType: sql.Int,
      require: true,
      default: StaticData.AUTH.Role.user,
    }),
    RefreshToken: new ModelSchemaValidator({
      name: "RefreshToken",
      sqlType: sql.VarChar,
    }),

    Expires: new ModelSchemaValidator({
      name: "Expires",
      sqlType: sql.DateTime,
    }),

    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
    }),
  },
  "Token",
  "CreatedAt"
);

module.exports = RefreshTokenSchema;
