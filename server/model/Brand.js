const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const sql = require("mssql");
const BrandSchema = new ModelSchema(
  {
    BrandID: new ModelSchemaValidator({
      name: "BrandID",
      sqlType: sql.Int,
    }),
    BrandName: new ModelSchemaValidator({
      name: "BrandName",
      sqlType: sql.NVarChar,
      require: true,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      require: true,
      default: new Date().toISOString(),
    }),
  },
  "Brand",
  "createAt"
);

module.exports = BrandSchema;
