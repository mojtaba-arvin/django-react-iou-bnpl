import React from 'react';
import { Route } from 'react-router-dom';
import { Admin, Resource, CustomRoutes } from 'react-admin';
import type { AdminAppProps } from '../../infrastructure/admin/config/admin-app.config';

/**
 * Shared AdminApp renders React-Admin with provided configuration,
 * resources, custom routes, and includes catchAll for error handling.
 */
export const AdminApp: React.FC<AdminAppProps> = ({
  theme,
  basename,
  authProvider,
  dataProvider,
  loginPage,
  dashboard,
  catchAll,
  resources,
  customRoutes = [],
}) => {
  return (
    <Admin
      theme={theme}
      basename={basename}
      authProvider={authProvider}
      dataProvider={dataProvider}
      loginPage={loginPage}
      dashboard={dashboard}
      catchAll={catchAll}
      requireAuth
    >
      {resources.map((res) => (
        <Resource
          key={res.name}
          name={res.name}
          list={res.list}
          edit={res.edit}
          create={res.create}
          show={res.show}
          recordRepresentation={res.recordRepresentation}
          options={res.options}
          icon={res.icon}
          {...res.props}
        />
      ))}
      {customRoutes.length > 0 && (
        <CustomRoutes noLayout>
          {customRoutes.map(({ path, element: Element }, idx) => (
            <Route key={path || idx} path={path} element={<Element />} />
          ))}
        </CustomRoutes>
      )}
    </Admin>
  );
};
