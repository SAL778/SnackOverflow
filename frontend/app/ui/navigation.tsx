import Link from 'next/link';
import Image from 'next/image';
import { ArrowTrendingUpIcon, PencilIcon, PowerIcon, RectangleStackIcon, UserIcon } from '@heroicons/react/24/outline';

// For creating the nav bar:
// https://github.com/vercel/next-learn/blob/main/dashboard/final-example/app/ui/dashboard/sidenav.tsx
// For mass creating the links in the bar:
// https://github.com/vercel/next-learn/blob/main/dashboard/final-example/app/ui/dashboard/nav-links.tsx
// snack overflow image source https://i.imgur.com/jSUHoMZ.png
function Links() {
    const objects = [
        {content: "Profile", href: "/profile", icon: UserIcon},
        {content: "Feed", href: "/feed", icon: RectangleStackIcon}, 
        {content: "Explore", href: "/explore", icon: ArrowTrendingUpIcon},
        {content: "New Post", href: "/newpost", icon: PencilIcon}
    ];

    var allLinks = []
    for (let object of objects) {
        const Icons = object.icon;
        allLinks.push(<Link
            key={object.content}
            href={object.href}
            className='flex h-[48px] grow items-center justify-center gap-2 bg-white p-3 text-sm font-medium hover:bg-orange-200 hover:text-orange-800 md:flex-none md:justify-start md:p-2 md:px-3'
          >
            <Icons className="w-6" />
            <p className="md:block">{object.content}</p>
        </Link>);
    }
    return <div>{allLinks}</div>;
}

export default function Navigation() {
    return (
      <div className="flex h-full flex-col px-3 py-4">
        <Link
          className="mb-2 flex h-20 items-end rounded-md bg-white p-4 shadow-md"
          href="/"
        >
          <div>
            <Image
                className="object-center"
                src="/snack-logo.png"
                alt="Snack Overflow icon"
                width={250}
                height={40}
			/>
          </div>
        </Link>
        <div className="flex grow flex-row justify-between space-x-2 shadow-md md:flex-col md:space-x-0">
        <Links/ >
        <div className="hidden h-auto w-full grow bg-white md:block"></div>
            <button className="flex h-[48px] w-full grow items-center rounded-md justify-center gap-2 bg-white shadow-md p-3 text-sm font-medium hover:bg-orange-200 hover:text-orange-800 md:flex-none md:justify-start md:p-2 md:px-3">
              <PowerIcon className="w-6" />
              <div className="hidden md:block">Sign Out</div>
            </button>
        </div>
      </div>
    );
  }