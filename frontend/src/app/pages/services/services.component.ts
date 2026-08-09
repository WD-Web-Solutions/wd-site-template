import { Component, ChangeDetectionStrategy } from '@angular/core';

import { UiCardComponent } from '../../shared/components/ui-card/ui-card.component';

import { SERVICES } from '../../core/data/services.data';

import { SeoService } from '../../core/services/seo.service';



@Component({

  selector: 'app-services',

  standalone: true,

  imports: [

    UiCardComponent

  ],

  templateUrl:

    './services.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:

    './services.component.css'

})
export class ServicesComponent {


  services = SERVICES;



  constructor(

    private seoService: SeoService

  ) {


    this.seoService.updatePage(

      'Commercial Asphalt & Surface Services | Your Company Name',

      'Professional asphalt, striping, coating, and commercial surface improvement services in your service area.'

    );


  }


}