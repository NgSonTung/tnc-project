const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const sql = require("mssql");
const CategorySchema = new ModelSchema(
  {
    CategoryID: new ModelSchemaValidator({
      name: "CategoryID",
      sqlType: sql.Int,
    }),
    CategoryName: new ModelSchemaValidator({
      name: "categoryName",
      sqlType: sql.NVarChar,
      require: true,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Category",
  "createAt"
);

module.exports = CategorySchema;
