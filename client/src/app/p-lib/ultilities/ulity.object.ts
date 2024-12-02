import { DomSanitizer } from '@angular/platform-browser';
export class Ps_UtilObjectService {
  private static sanitizer: DomSanitizer;
  //hàm kiểm tra giá trị
  public static hasValue(value: any): boolean {
    return !(value === undefined || value === null);
  }
  //hàm kiểm tra giá trị mảng
  public static hasListValue(value: any): boolean {
    return !(value === undefined || value === null || value.length === 0);
  }
  //hàm kiểm tra giá trị chuỗi
  public static hasValueString(value: any): boolean {
    return !(value === undefined || value === null || value === '');
  }
  //hàm kiểm tra ngày hợp lệ
  public static isValidDate(value: any): boolean {
    return (
      Ps_UtilObjectService.hasValueString(value) &&
      isNaN(value) &&
      (value instanceof Date || new Date(value) instanceof Date) &&
      (!isNaN(value.valueOf()) || !isNaN(new Date(value).valueOf()))
    );
  }
  //hàm kiểm tra ngày hợp lệ value có kiểu là ngày hoặc chuỗi
  public static isValidDate2(value: Date | string): boolean {
    // var rs1 = Ps_UtilObjectService.hasValueString(value)
    // var rs2 = isNaN(value)
    // var rs21 = Number.isNaN(value)
    var rs22 = isNaN(+value);
    var rs23 = Number.isNaN(+value);
    // var rs3 = value instanceof Date
    // var rs4 = new Date(value) instanceof Date
    // var rs5 = Number.isNaN(value.valueOf())
    // var rs6 = Number.isNaN(new Date(value).valueOf())

    console.log('rs', rs22, rs23);
    //nếu là Date hoặc string
    if (value instanceof Date || typeof value === 'string')
      //dùng Number.isNaN(+) để check có phải khác số VÀ có
      return (
        Ps_UtilObjectService.hasValueString(value) &&
        isNaN(+value) &&
        (value instanceof Date || new Date(value) instanceof Date) &&
        // !Number.isNaN(value.valueOf()) || !Number.isNaN(new Date(value).valueOf())
        (!isNaN(+value.valueOf()) || !isNaN(new Date(value).valueOf()))
      );
    else return false;
  }
  //hàm chuyển ngày thành chuỗi
  public static parseDateToString = function (
    key,
    value,
    dateArr: string[] = []
  ) {
    if (Ps_UtilObjectService.isValidDate(value)) {
      if (dateArr.findIndex((s) => s == key) != -1) {
        var date = new Date(value);
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        return date.toDateString();
      }
    }
    return value;
  };
  //hàm chuyển ngày giờ địa phương thành chuỗi
  public static parseLocalDateTimeToString = function (
    key,
    value,
    dateArr: string[] = [],
    dateTimeArr: string[] = []
  ) {
    if (Ps_UtilObjectService.isValidDate(value)) {
      if (dateTimeArr.findIndex((s) => s == key) != -1)
        return (
          new Date(value).toDateString() +
          ' ' +
          new Date(value).toLocaleTimeString([], { hour12: false })
        );
      else if (dateArr.findIndex((s) => s == key) != -1) {
        var date = new Date(value);
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        return date.toDateString();
      }
    }
    return value;
  };
  //hàm chuyển giở địa phương thành chuỗi
  public static parseLocalTimeToString = function (
    key,
    value,
    timeArr: string[] = []
  ) {
    if (Ps_UtilObjectService.isValidDate(value)) {
      if (timeArr.findIndex((s) => s == key) != -1)
        return new Date(value).toLocaleTimeString([], { hour12: false });
    }
    return value;
  };
  //hàm lấy tên file từ chuỗi blob
  public static getFileName(disposition: string): string {
    const utf8FilenameRegex = /filename\*=UTF-8''([\w%\-\.]+)(?:; ?|$)/i;
    const asciiFilenameRegex = /filename=(["']?)(.*?[^\\])\1(?:; ?|$)/i;

    let fileName: string = null;
    if (utf8FilenameRegex.test(disposition)) {
      fileName = decodeURIComponent(utf8FilenameRegex.exec(disposition)[1]);
    } else {
      const matches = asciiFilenameRegex.exec(disposition);
      if (matches != null && matches[2]) {
        fileName = matches[2];
      }
    }
    return fileName;
  }
  //hàm lấy ảnh từ server hachihachi
  public static getImgRes(url: string) {
    var imgRes = 'http://172.16.10.251:89/';
    var imgHachi = 'hachihachi.com';

    if (Ps_UtilObjectService.hasValueString(url)) {
      if (
        url.includes('~/') &&
        !url.includes(imgRes) &&
        !url.includes(imgHachi)
      )
        return url.replace('~/', imgRes); //bị undefined DTOConfig.appInfo.res
      else if (
        url.includes('~/') &&
        (url.includes(imgRes) || url.includes(imgHachi))
      )
        return url.replace('~/', '/');
      else if (!url.includes(imgRes) && !url.includes(imgHachi))
        return imgRes + url; //"http://172.16.10.251:89/"
      else return url;
    } else return url;
  }
  //hàm lấy ảnh từ server pool
  public static getImgResHachi(url: string) {
    var imgRes = '172.16.10.251';

    var imgHachi = 'https://hachihachi.com.vn/';

    if (Ps_UtilObjectService.hasValueString(url)) {
      if (
        url.includes('~/') &&
        !url.includes(imgRes) &&
        !url.includes(imgHachi)
      )
        return url.replace('~/', imgHachi); //bị undefined DTOConfig.appInfo.res
      else if (
        url.includes('~/') &&
        (url.includes(imgRes) || url.includes(imgHachi))
      )
        return url.replace('~/', '/');
      else if (!url.includes(imgRes) && !url.includes(imgHachi))
        return imgHachi + url;
      else return url;
    } else return url;
  }
  //hàm thêm ngày
  public static addDays = function (date: Date, d) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() + d * 24 * 60 * 60 * 1000);
    return newDate;
  };
  //hàm thêm giờ
  public static addHours = function (date: Date, h) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() + h * 60 * 60 * 1000);
    return newDate;
  };
  //hàm thêm phút
  public static addMinutes = function (date: Date, m) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() + m * 60 * 1000);
    return newDate;
  };
  //hàm trừ ngày
  public static subtractDays = function (date: Date, d) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() - d * 24 * 60 * 60 * 1000);
    return newDate;
  };
  //hàm trừ giờ
  public static subtractHours = function (date: Date, h) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() - h * 60 * 60 * 1000);
    return newDate;
  };
  //hàm trừ phút
  public static subtractMinutes = function (date: Date, m) {
    var newDate = new Date(date);
    newDate.setTime(newDate.getTime() - m * 60 * 1000);
    return newDate;
  };
  //hàm tìm số ngày chênh lệch giữa 2 ngày
  public static getDaysDiff(
    date1: Date | string,
    date2: Date | string
  ): number {
    return (
      Math.abs(new Date(date1).valueOf() - new Date(date2).valueOf()) /
      (1000 * 60 * 60 * 24)
    );
  }
  //hàm tìm số ngày còn lại giữa 2 ngày
  public static getDaysLeft(start: Date | string, end: Date | string): number {
    return (
      (new Date(end).valueOf() - new Date(start).valueOf()) /
      (1000 * 60 * 60 * 24)
    );
  }
  //hàm sao chép từ fromObj sang toObj nếu trường p tồn tại
  public static copyProperty(fromObj, toObj) {
    for (const p in fromObj) toObj[p] = (p in toObj ? toObj : fromObj)[p];
  }
  //hàm sao chép từ fromObj sang toObj, nếu trường p ko tồn tại thì tạo p trong toObj
  public static copyPropertyForce(fromObj, toObj) {
    for (const p in fromObj) toObj[p] = fromObj[p];
  }
  //hàm callback thoát khỏi RegEx để dùng cho replaceAll
  public static escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
  }
  //hàm thay tất cả chuỗi
  public static replaceAll(str, find, replace) {
    return str.replace(new RegExp(this.escapeRegExp(find), 'g'), replace);
  }

  public static convertListBase64ToURL(listBase64Data: Array<string>) {
    let listURL: Array<string> = [];
    listBase64Data.forEach((element) => {
      listURL.push(this.convertBase64ToURL(element));
    });
    console.log(listURL);
    return listURL;
  }
  private static convertBase64ToURL(base64Data: string): string {
    const byteArr = new Uint8Array(
      atob(base64Data)
        .split('')
        .map((char) => char.charCodeAt(0))
    );
    const file = new Blob([byteArr], { type: 'image/jpeg' });
    const url = URL.createObjectURL(file);
    const imageURL = this.sanitizer.bypassSecurityTrustResourceUrl(url);
    return imageURL.toString();
  }
}
