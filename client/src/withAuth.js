// Mark the component as a client-side component
"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { isAuthenticated } from "@/utils/auth";

const withAuth = (WrappedComponent) => {
  const ComponentWithAuth = (props) => {
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
      // Check if the user is authenticated
      if (!isAuthenticated()) {
        // Redirect to login page if not authenticated
        router.push("/");
      } else if (
        (pathname.startsWith("/dashboard"))
      ) {
        router.push(pathname);
      }
    }, [router, pathname]);

    // If authenticated, render the wrapped component
    return <WrappedComponent {...props} />;
  };

  ComponentWithAuth.displayName = `WithAuth(${
    WrappedComponent.displayName || WrappedComponent.name || "Component"
  })`;

  return ComponentWithAuth;
};

export default withAuth;
