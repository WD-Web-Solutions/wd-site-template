import { Injectable } from '@angular/core';

import {
  Title,
  Meta
} from '@angular/platform-browser';



@Injectable({

  providedIn: 'root'

})
export class SeoService {


  constructor(

    private title: Title,

    private meta: Meta

  ) {}



  updatePage(

    title: string,

    description: string

  ): void {


    this.title.setTitle(title);



    this.meta.updateTag({

      name: 'description',

      content: description

    });



    this.meta.updateTag({

      property: 'og:title',

      content: title

    });



    this.meta.updateTag({

      property: 'og:description',

      content: description

    });


  }


}