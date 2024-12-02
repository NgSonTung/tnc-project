export class DTOStatus {
  StatusID: number;
  StatusName: string;
  TypeStatus: string;
  Mark: string;
  CreatedAt: string;

  constructor(
    statusID: number,
    statusName: string,
    typeStatus: string,
    mark: string,
    createdAt: string
  ) {
    this.StatusID = statusID;
    this.StatusName = statusName;
    this.TypeStatus = typeStatus;
    this.Mark = mark;
    this.CreatedAt = createdAt;
  }
}
