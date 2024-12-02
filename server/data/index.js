import products from './products.json';

export const customerSlidersImg = [
    { url: 'https://thanhmobile.vn/uploads/plugin/gallery/180/nh-khach-hang-11-4.jpg', id: '1', alt: 'KH1' },
    {
        url: 'https://thanhmobile.vn/uploads/plugin/gallery/182/nh-khach-hang-13-6.jpg',
        id: '2',
        alt: 'KH2',
    },
    { url: 'https://thanhmobile.vn/uploads/plugin/gallery/181/nh-khach-hang-12-5.jpg', id: '3 ', alt: 'KH3' },
    {
        url: 'https://thanhmobile.vn/uploads/plugin/gallery/172/nh-khach-hang-7-z3751164352388-38423d4ad3155197cba02fdb0e2efce3.jpg',
        id: '4',
        alt: 'KH4',
    },
    { url: 'https://thanhmobile.vn/uploads/plugin/gallery/180/nh-khach-hang-11-4.jpg', id: '1', alt: 'KH1' },
    {
        url: 'https://thanhmobile.vn/uploads/plugin/gallery/182/nh-khach-hang-13-6.jpg',
        id: '2',
        alt: 'KH2',
    },
];

export const sliderBannerImgs = [
    'https://regmedia.co.uk/2022/03/21/supplied_zenbook_duo.jpg',
    'https://genk.mediacdn.vn/2017/xiaomi-mimix-xach-tay-gia-re-1484678116153.jpg',
    'https://cdn.sforum.vn/sforum/wp-content/uploads/2022/09/MacBook-Pro-2022-7.jpg',
    'https://cdn1.hoanghamobile.com/tin-tuc/wp-content/uploads/2022/06/Blue-Futuristic-Top-Future-Technologies-YouTube-Thumbnail.png',
];

export const phone = products.filter((item) => item.category === 'phone');
