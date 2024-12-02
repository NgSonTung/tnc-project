module.exports = class DTOLS_Status {
  constructor(data) {
    this.StatusID = data.StatusID;
    this.StatusName = data.StatusName;
    this.TypeStatus = data.TypeStatus;
    this.Mark = data.Mark ?? null;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
