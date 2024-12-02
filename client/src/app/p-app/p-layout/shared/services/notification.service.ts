import { Injectable } from '@angular/core';
import { NotificationService } from '@progress/kendo-angular-notification';

@Injectable({ providedIn: 'root' })
export class NotificationPopupService {
  hideAfter: number = 2000;
  constructor(private notificationSerivce: NotificationService) {}

  public onSuccess(content: string): void {
    this.notificationSerivce.show({
      content: content,
      cssClass: 'button-notification',
      animation: { type: 'fade', duration: 200 },
      position: { horizontal: 'center', vertical: 'top' },
      type: { style: 'success', icon: true },
      hideAfter: this.hideAfter,
    });
  }

  public onError(content: string): void {
    this.notificationSerivce.show({
      content: content,
      cssClass: 'button-notification',
      animation: { type: 'fade', duration: 200 },
      position: { horizontal: 'center', vertical: 'top' },
      type: { style: 'error', icon: true },
      hideAfter: this.hideAfter,
    });
  }
}
