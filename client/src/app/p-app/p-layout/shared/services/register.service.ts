import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class RegisterService {
  private registerShownSubject: BehaviorSubject<boolean> =
    new BehaviorSubject<boolean>(false);

  registerShown$ = this.registerShownSubject.asObservable();

  toggleRegisterShown(): void {
    const currentValue = this.registerShownSubject.getValue();
    this.registerShownSubject.next(!currentValue);
  }

  openRegisterForm(): void {
    this.registerShownSubject.next(true);
  }

  closeRegisterForm(): void {
    this.registerShownSubject.next(false)
  }
}
