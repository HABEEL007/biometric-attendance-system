import { useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/': return 'Dashboard';
      case '/live-monitor': return 'Live Monitor';
      case '/staff': return 'Staff Management';
      case '/enrollment': return 'Enrollment';
      case '/records': return 'Records';
      case '/audit-logs': return 'Audit Logs';
      case '/settings': return 'Settings';
      default: return 'BioAttend';
    }
  };

  return (
    <header className="flex justify-between items-center h-16 px-margin-desktop w-full sticky top-0 z-10 bg-surface-container border-b border-outline-variant">
      <div className="font-headline-md text-headline-md font-bold text-primary">
        {getPageTitle(location.pathname)}
      </div>
      <div className="flex items-center gap-4">
        <button className="material-symbols-outlined p-2 rounded-full hover:bg-surface-variant transition-colors">dark_mode</button>
        <button className="material-symbols-outlined p-2 rounded-full hover:bg-surface-variant transition-colors">notifications</button>
        <div className="w-8 h-8 rounded-full bg-surface-variant overflow-hidden">
          <img alt="Administrator Profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDDSu9lBiMY1yQ_fSSa_S3NgBxxpaADo4pCQcxfP-wBf9w0SUXoqy18nPrjZuytfq3X5DghpgarCgc5gnthb-dAgOOurO0IX3extYlrpUhW1D_yDtElKov7R2wGKN_La8ZpifLUeXNE6n4IHDCUnGM4dkce3A34v8Fr_YWYsErFt0d9plQ62Js96i6LUw_3ytOzFiqdJ_q908pgqQaB9qL9tgPW3nbus4CXy467s_knQaQyJPCILQNpKvE95eFLA_vYe8IEKt2pPbHf"/>
        </div>
      </div>
    </header>
  );
};

export default Header;
