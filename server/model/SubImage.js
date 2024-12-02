const sql = require("mssql");
const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");

const SubImageSchema = new ModelSchema(
  {
    SubimgID: new ModelSchemaValidator({
      name: "SubimgID",
      sqlType: sql.Int,
    }),

    Image: new ModelSchemaValidator({
      name: "Image",
      sqlType: sql.VarChar,
      require: true,
    }),

    Alt: new ModelSchemaValidator({
      name: "Alt",
      sqlType: sql.VarChar,
      require: true,
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
  "Subimg",
  "createAt"
);

module.exports = SubImageSchema;
