const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const sql = require("mssql");

const FeatureSchema = new ModelSchema(
  {
    FeatureID: new ModelSchemaValidator({
      name: "FeatureID",
      sqlType: sql.Int,
    }),
    Feature: new ModelSchemaValidator({
      name: "Feature",
      sqlType: sql.NVarChar,
      require: true,
      default: "",
    }),
    ProductID: new ModelSchemaValidator({
      name: "ProductID",
      sqlType: sql.Int,
      require: true,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "feature",
  "createAt"
);
module.exports = FeatureSchema;
