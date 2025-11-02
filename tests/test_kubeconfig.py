import yaml
import os
import unittest

class TestKubeconfig(unittest.TestCase):
    def test_kubeconfig_structure(self):
        """Test that kubeconfig has the basic required structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check basic structure
        self.assertIn('apiVersion', config)
        self.assertIn('clusters', config)
        self.assertIn('contexts', config)
        self.assertIn('users', config)
        self.assertIn('current-context', config)
        self.assertIn('kind', config)
        
        # Check that it's a Config kind
        self.assertEqual(config['kind'], 'Config')
        
        # Check that we have at least one cluster
        self.assertGreater(len(config['clusters']), 0)
        
        # Check that we have at least one user
        self.assertGreater(len(config['users']), 0)
        
        # Check that we have at least one context
        self.assertGreater(len(config['contexts']), 0)
        
    def test_cluster_config(self):
        """Test cluster configuration structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)
            
        cluster = config['clusters'][0]['cluster']
        
        # Check that server is defined
        self.assertIn('server', cluster)
        
        # Check that certificate-authority-data is defined
        self.assertIn('certificate-authority-data', cluster)
        
    def test_user_config(self):
        """Test user configuration structure"""
        kubeconfig_path = os.path.join(os.path.dirname(__file__), '..', 'kubeconfig-jenkins.yaml')
        
        with open(kubeconfig_path, 'r') as f:
            config = yaml.safe_load(f)
            
        user = config['users'][0]['user']
        
        # Check that some form of authentication is defined
        # (token, cert, etc.)
        auth_methods = ['token', 'client-certificate-data', 'username', 'exec']
        self.assertTrue(any(method in user for method in auth_methods), 
                       "No authentication method found in user config")

if __name__ == '__main__':
    unittest.main()