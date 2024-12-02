import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  constructor(private http: HttpClient) {}

  addChat(sessionId: string, message: string): Observable<any> {
    const body = message;
    console.log('BODY', { msg: body });

    return this.http.post('/api/v1/chatbot/chat/1', { msg: body });
  }

  getImage(imageName: string): Observable<any> {
    return this.http
      .get('/api/v1/chat/image/' + imageName, { responseType: 'blob' })
      .pipe(
        map((baseImage: Blob) => {
          let objectURL = URL.createObjectURL(baseImage);
          return objectURL;
        })
      )
      .pipe(catchError(this.handleError));
  }

  private handleError(e: any) {
    return throwError(() => new Error(e));
  }
}
