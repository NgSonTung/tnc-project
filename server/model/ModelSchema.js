class ModelSchema {
  constructor(schema, schemaName, defaultSort) {
    this.schema = schema;
    this.schemaName = schemaName;
    this.defaultSort = defaultSort;
  }

  validateData(data) {
    for (let fieldName in this.schema) {
      let val = data[fieldName];

      let field = this.schema[fieldName];
      if (val === undefined || val === null) {
        data[fieldName] = field.default;
      }
      let {isValid, err} = field.validate(val);
      if (!isValid) {
        throw new Error("Invalid data at field: " + fieldName + ". " + err);
      }
    }
    return data;
  }
}

module.exports = ModelSchema;
