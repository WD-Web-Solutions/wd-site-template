import { Service } from '../models/service.model';



export const SERVICES: Service[] = [

  {
    title: 'Asphalt Services',

    slug: 'asphalt-services',

    category: 'Asphalt',

    description:
      'Professional asphalt installation, repairs, maintenance, and restoration solutions for commercial properties.',

    details:
      'Your Company Name provides commercial asphalt solutions designed to improve safety, appearance, and longevity. Our services include asphalt repairs, resurfacing, maintenance, and property improvements.',

    icon:
      'road',

    image:
      '/assets/images/services/asphalt.svg'

  },


  {
    title: 'Parking Lot Striping',

    slug: 'parking-lot-striping',

    category: 'Striping',

    description:
      'Professional parking lot layouts, ADA compliance markings, and safety striping solutions.',

    details:
      'Our parking lot striping services help businesses maintain safe, organized, and professional-looking properties. We provide layouts, ADA markings, re-striping, and custom parking solutions.',

    icon:
      'square-parking',

    image:
      '/assets/images/services/striping.svg'

  },


  {
    title: 'Concrete Services',

    slug:
      'concrete-services',

    category:
      'Concrete',

    description:
      'Concrete repair, replacement, and improvement services designed for commercial properties.',

    details:
      'From repairs to new installations, Your Company Name delivers durable concrete solutions built for commercial environments.',

    icon:
      'trowel',

    image:
      '/assets/images/services/concrete.svg'

  },


  {
    title:
      'Surface Coatings',

    slug:
      'surface-coatings',

    category:
      'Coatings',

    description:
      'Durable protective coatings designed to extend the life of commercial surfaces.',

    details:
      'Protective coatings help commercial properties maintain durability, appearance, and resistance against heavy traffic and weather conditions.',

    icon:
      'shield-alt',

    image:
      '/assets/images/services/coatings.svg'

  }

];