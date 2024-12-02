import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'tnc-project';

  loggedIn: boolean = true;
  showLogin: boolean = true;
  showChat: boolean = false;

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
