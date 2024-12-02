module.exports = class DTOAuth {
  constructor(data) {
    this.AuthID = data.AuthID;
    this.AuthName = data.AuthName;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
