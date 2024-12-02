import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class CartService {
  isCartPopUpOpened: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(
    false
  );

  getIsCartPopUpState() {
    return this.isCartPopUpOpened.asObservable();
  }

  onToggleCartPopUpState(value: boolean) {
    this.isCartPopUpOpened.next(value);
  }
}
