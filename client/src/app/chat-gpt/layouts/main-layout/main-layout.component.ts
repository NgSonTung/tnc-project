import { Component } from '@angular/core';

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.scss'],
})
export class MainLayoutComponent {
  loggedIn: boolean = true;
  showLogin: boolean = true;
  showChat: boolean = true;

  toggleShowChat() {
    this.showChat = !this.showChat;
  }

  toggleShowLogin() {
    this.loggedIn
      ? (this.showLogin = false)
      : (this.showLogin = !this.showLogin);
  }

  handleLoginSuccess() {
    this.loggedIn = true;
    this.toggleShowLogin();
  }
}
